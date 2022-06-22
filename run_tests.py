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

def _run_test_once(TestType, logfile: str, image_path: str | None = None):
    test = TestType()

    test._set_ipc_duration(args.ipc_timeout)
    status, msg = test.prepare()
    if status != wftest.Status.OK:
        return status, msg

    result = test.run(args.wayfire, logfile)
    if image_path:
        err_msg = wu.take_screenshot(test.socket, image_path)
        if err_msg:
            test.cleanup()
            return wftest.Status.CRASHED, "Could not take a screenshot: " + err_msg

    test.cleanup()
    return result

def run_test_once(TestType, logfile: str, image_path: str | None = None):
    try:
        actual_log = '/dev/stdout' if args.show_log else logfile
        return _run_test_once(TestType, actual_log, image_path)
    except:
        return wftest.Status.CRASHED, "Test runner crashed " + traceback.format_exc()

def run_single_test(testMain) -> Tuple[wftest.Status, str | None]:
    spec = importlib.util.spec_from_file_location("main", testMain)
    assert spec is not None
    assert spec.loader is not None
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo) # type:ignore

    # Go to the directory of the test, so that any temporary files are stored there
    # and so that the wayfire.ini file can be found easily
    cwd = os.getcwd()
    os.chdir(testMain[:-7]) # Ending is always main.py, so if we drop it, we get the test dir

    status = wftest.Status.OK
    msg = None


    if foo.is_gui() and not args.compare_with: # type: ignore
        status, msg = wftest.Status.SKIPPED, 'GUI test need a second Wayfire executable via --compare-with'
    elif foo.is_gui(): # type: ignore
        status, msg = run_test_once(foo.WTest, 'wayfireA.log', 'wayfireA.png') # type: ignore
        msg = 'wayfireA: ' + msg
        if status == wftest.Status.OK:
            status, msg = run_test_once(foo.WTest, 'wayfireB.log', 'wayfireB.png') # type: ignore
            msg = 'wayfireB: ' + msg
            if status == wftest.Status.OK:
                code = wu.compare_images('wayfireA.png', 'wayfireB.png')
                if code == wu.ImageDiff.SAME:
                    status, msg = wftest.Status.OK, None
                elif code == wu.ImageDiff.SIZE_MISMATCH:
                    status, msg = wftest.Status.WRONG, 'Screenshot sizes are different.'
                else:
                    status, msg = wftest.Status.WRONG, 'Screenshots are different.'
    else:
        status, msg = run_test_once(foo.WTest, 'wayfire.log') # type: ignore

    os.chdir(cwd)
    return status, msg

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
