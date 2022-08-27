#!/bin/env python3

import argparse
import os
import sys
import glob
import importlib.util

from termcolor import colored
from typing import Tuple
from wfpytest import wftest
import wfutil as wu
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('testdir', type=str)
parser.add_argument('wayfire', type=str)
parser.add_argument('--compare-with', type=str, required=False)
parser.add_argument('--show-log', action='store_true', required=False)
parser.add_argument('--ipc-timeout', type=float, default=0.1, required=False)
args = parser.parse_args()

# Make tests execute slower or faster

def check_exec(path):
    if not os.access(path, os.X_OK):
        print("The given wayfire binary \"" + path + "\" is not executable!")
        sys.exit(-1)

def check_arguments():
    check_exec(args.wayfire)
    if args.compare_with:
        check_exec(args.compare_with)

class TestResult:
    def __init__(self, status, msg, file_list):
        self.status = status
        self.msg = msg
        self.file_list = file_list

def _run_test_once(TestType, wayfire_exe, logfile: str, image_prefix: str) -> TestResult:
    test = TestType()

    test.screenshot_prefix = image_prefix
    test._set_ipc_duration(args.ipc_timeout)
    status, msg = test.prepare()
    if status != wftest.Status.OK:
        return TestResult(status, msg, [])

    try:
        status, msg = test.run(wayfire_exe, logfile)
        test.cleanup()
        return TestResult(status, msg, test.screenshots)
    except KeyboardInterrupt:
        test.cleanup()
        raise
    except:
        test.cleanup()
        return TestResult(wftest.Status.CRASHED, "Test runner crashed " + traceback.format_exc(), [])

def run_test_once(test_main_file, TestType, wayfire_exe, logfile: str, image_prefix: str) -> TestResult:
    # Go to the directory of the test, so that any temporary files are stored there
    # and so that the wayfire.ini file can be found easily
    cwd = os.getcwd()
    test_home_dir = test_main_file[:-7]
    os.chdir(test_home_dir) # Ending is always main.py, so if we drop it, we get the test dir

    actual_log = '/dev/stdout' if args.show_log else logfile
    result = _run_test_once(TestType, wayfire_exe, actual_log, os.getcwd() + '/' + image_prefix)
    os.chdir(cwd)
    return result

def run_single_test(testMain) -> Tuple[wftest.Status, str | None]:
    spec = importlib.util.spec_from_file_location("main", testMain)
    assert spec is not None
    assert spec.loader is not None
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo) # type:ignore

    if foo.is_gui() and args.compare_with: # type: ignore
        resultA = run_test_once(testMain, foo.WTest, args.wayfire, 'wayfireA.log', 'wayfireA') # type: ignore
        if resultA.status != wftest.Status.OK:
            return resultA.status, 'wayfireA: ' + str(resultA.msg)

        resultB = run_test_once(testMain, foo.WTest, args.compare_with, 'wayfireB.log', 'wayfireB') # type: ignore
        if resultB.status != wftest.Status.OK:
            return resultA.status, 'wayfireB: ' + str(resultA.msg)

        if len(resultA.file_list) != len(resultB.file_list):
            return wftest.Status.WRONG, 'Test returns different amount of images?' + \
                    str(resultA.file_list) + ' vs. ' + str(resultB.file_list)

        for (fileA, fileB) in zip(resultA.file_list, resultB.file_list):
            code = wu.compare_images(fileA, fileB, fileA + '.delta.png', 0.01)
            if code == wu.ImageDiff.SIZE_MISMATCH:
                return wftest.Status.WRONG, 'Screenshot sizes are different: ' + fileA + ' vs. ' + fileB
            elif code == wu.ImageDiff.DIFFERENT:
                return wftest.Status.WRONG, 'Screenshots are different: ' + fileA + ' vs. ' + fileB

        return wftest.Status.OK, None

    elif not foo.is_gui():
        result = run_test_once(testMain, foo.WTest, args.wayfire, 'wayfire.log', '') # type: ignore
        return result.status, result.msg
    else:
        return wftest.Status.SKIPPED, 'GUI test needs --compare-with'

tests_ok = 0
tests_wrong = 0
tests_skip = 0

def run_all_tests():
    global tests_ok
    global tests_wrong
    global tests_skip

    print("Running tests in directory " + colored(args.testdir, "yellow"))
    for filename in glob.iglob(args.testdir + '/**/main.py', recursive=True):
        print("Running test " + colored(filename, 'blue') + " - ", end='')
        status, explanation = run_single_test(filename)

        if status == wftest.Status.OK:
            tests_ok += 1
        elif status == wftest.Status.SKIPPED:
            tests_skip += 1
        else:
            tests_wrong += 1

        message, color = status.value
        print(colored(message, color, attrs=['bold']), end='')
        if explanation:
            print(" (" + explanation + ")")
        else:
            print()

check_arguments()
run_all_tests()

# Print summary

tests_total = tests_ok + tests_skip + tests_wrong

text_ok=colored(str(tests_ok) + " ok", 'green' if tests_wrong == 0 else 'blue', attrs=['bold'])
text_wrong="0 not ok" if tests_wrong == 0 else colored(str(tests_wrong) + " not ok", 'red', attrs=['bold'])
text_skipped="0 skipped" if tests_skip == 0 else colored(str(tests_skip) + " skipped", 'yellow', attrs=['bold'])
print("Test summary: {} / {} / {}".format(text_ok, text_wrong, text_skipped))
