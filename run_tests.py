#!/bin/env python3

import argparse
import json
import os
import shlex
import sys
import glob
import importlib.util
import time
from multiprocessing import Pool

from termcolor import colored
from typing import Tuple, List
from wfpytest import wftest
import wfutil as wu
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('testdir', type=str)
parser.add_argument('wayfire', type=str)
parser.add_argument('--compare-with', type=str, required=False)
parser.add_argument('--show-log', action='store_true', required=False)
parser.add_argument('--ipc-timeout', type=float, default=0.1, required=False)
parser.add_argument('--failscript', action='store_true', required=False)
parser.add_argument('--categories', type=str, default='', required=False)
parser.add_argument('--force-gui', action='store_true', required=False)
parser.add_argument('-j', type=int, default='1', required=False)
parser.add_argument('--maxretries', type=int, default='1', required=False)
parser.add_argument('--configuration', type=str, default=None, required=False)
parser.add_argument('--failscript-previous', action='append', default=[], help=argparse.SUPPRESS)
parser.add_argument('--failscript-test', action='append', default=[], help=argparse.SUPPRESS)

# Make tests execute slower or faster

class TestResult:
    def __init__(self, status, msg, file_list):
        self.status = status
        self.msg = msg
        self.file_list = file_list

def _run_test_once(args: argparse.Namespace, TestType, wayfire_exe, logfile: str, image_prefix: str, timeoutMultiplier: float) -> TestResult:
    test = TestType()

    test.screenshot_prefix = image_prefix
    test._set_ipc_duration(args.ipc_timeout * timeoutMultiplier)
    status, msg = test.prepare()
    if status != wftest.Status.OK:
        return TestResult(status, msg, [])

    try:
        status, msg = test.run(wayfire_exe, logfile, args.configuration)
        test.cleanup()
        return TestResult(status, msg, test.screenshots)
    except KeyboardInterrupt:
        test.cleanup()
        raise
    except:
        test.cleanup()
        return TestResult(wftest.Status.CRASHED, "Test runner crashed " + traceback.format_exc(), [])

def get_test_base_dir(test_main_file: str):
    # Ending is always main.py, so if we drop it, we get the test dir
    return test_main_file[:-7]

def get_repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def get_launcher_path() -> str:
    return os.environ.get('WF_TEST_LAUNCHER', os.path.join(get_repo_root(), 'run_tests.sh'))

def encode_failed_test(test: 'FailedTest') -> str:
    return json.dumps([test.prefix, test.gui])

def decode_failed_test(raw: str) -> 'FailedTest':
    prefix, gui = json.loads(raw)
    return FailedTest(prefix, gui)

def format_shell_array(items: List[str], indent: str = '    ') -> str:
    if not items:
        return '()'

    joined = '\n'.join(f"{indent}{shlex.quote(item)}" for item in items)
    return f"(\n{joined}\n)"

def get_runner_args(args: argparse.Namespace) -> List[str]:
    cli_args: List[str] = []

    if args.compare_with:
        cli_args.extend(['--compare-with', args.compare_with])
    if args.categories:
        cli_args.extend(['--categories', args.categories])
    if args.force_gui:
        cli_args.append('--force-gui')

    cli_args.extend(['-j', str(args.j)])

    if args.configuration is not None:
        cli_args.extend(['--configuration', args.configuration])
    if args.ipc_timeout != 0.1:
        cli_args.extend(['--ipc-timeout', str(args.ipc_timeout)])

    return cli_args

def write_failscript(args: argparse.Namespace) -> str:
    script_path = os.path.join(get_repo_root(), 'rerun_failed_tests.sh')
    launcher = get_launcher_path()
    fixed_args = get_runner_args(args)
    failed_prefixes = [test.prefix for test in failed_tests]
    failed_gui = ['1' if test.gui else '0' for test in failed_tests]
    previous_failures = [encode_failed_test(test) for test in failed_tests]

    script = f'''#!/bin/bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

LAUNCHER={shlex.quote(launcher)}
TESTDIR={shlex.quote(args.testdir)}
WAYFIRE={shlex.quote(args.wayfire)}
FIXED_ARGS={format_shell_array(fixed_args)}
FAILED_TESTS={format_shell_array(failed_prefixes)}
FAILED_IS_GUI={format_shell_array(failed_gui)}
PREVIOUS_FAILURES={format_shell_array(previous_failures)}

usage() {{
    cat <<'EOF'
Usage:
  ./rerun_failed_tests.sh
  ./rerun_failed_tests.sh list
  ./rerun_failed_tests.sh show <index>
  ./rerun_failed_tests.sh run [slow|sloow] [log] <index|all|all-parallel>
EOF
}}

show_failed_tests() {{
    if [ ${{#FAILED_TESTS[@]}} -eq 0 ]; then
        printf 'No failing tests recorded.\\n'
        return
    fi

    printf 'Failed tests:\\n'
    local idx
    for idx in "${{!FAILED_TESTS[@]}}"; do
        printf '%s. %s\\n' "$idx" "${{FAILED_TESTS[$idx]%/main.py}}"
    done
}}

require_index() {{
    local idx=$1
    if ! [[ "$idx" =~ ^[0-9]+$ ]] || [ "$idx" -lt 0 ] || [ "$idx" -ge "${{#FAILED_TESTS[@]}}" ]; then
        printf 'Wrong selection!\\n' >&2
        exit 1
    fi
}}

show_test() {{
    local idx=$1
    local path="${{FAILED_TESTS[$idx]%/main.py}}"

    if [ "${{FAILED_IS_GUI[$idx]}}" = "1" ]; then
        DISPLAY="${{OLD_DISPLAY:-${{DISPLAY:-}}}}" WAYLAND_DISPLAY="${{OLD_WAYLAND_DISPLAY:-${{WAYLAND_DISPLAY:-}}}}" eog "$path"/*.png
    else
        "${{EDITOR:-vi}}" "$path"/*.log
    fi
}}

run_tests() {{
    local mode=$1
    shift

    if [ ${{#FAILED_TESTS[@]}} -eq 0 ]; then
        printf 'No failing tests recorded.\\n'
        return
    fi

    local extra_args=()
    local selected_tests=()

    while [ $# -gt 0 ]; do
        case "$1" in
            --)
                shift
                break
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    if [ "$mode" = "all" ]; then
        local idx
        for idx in "${{!FAILED_TESTS[@]}}"; do
            selected_tests+=("${{FAILED_TESTS[$idx]}}")
        done
    elif [ "$mode" = "all-parallel" ]; then
        local idx
        for idx in "${{!FAILED_TESTS[@]}}"; do
            selected_tests+=("${{FAILED_TESTS[$idx]}}")
        done
    else
        require_index "$mode"
        selected_tests+=("${{FAILED_TESTS[$mode]}}")
    fi

    local cmd=("$LAUNCHER")
    local previous
    cmd+=("$TESTDIR")
    cmd+=("$WAYFIRE")
    cmd+=("${{FIXED_ARGS[@]}}")
    cmd+=(--maxretries 1)
    cmd+=(--failscript)

    for previous in "${{PREVIOUS_FAILURES[@]}}"; do
        cmd+=(--failscript-previous "$previous")
    done

    local selected_test
    for selected_test in "${{selected_tests[@]}}"; do
        cmd+=(--failscript-test "$selected_test")
    done

    if [ "$mode" = "all" ]; then
        cmd+=(-j 1)
    fi

    cmd+=("${{extra_args[@]}}")
    "${{cmd[@]}}"
}}

if [ $# -eq 0 ]; then
    show_failed_tests
    exit 0
fi

case "$1" in
    list)
        show_failed_tests
        ;;
    show)
        if [ $# -ne 2 ]; then
            usage
            exit 1
        fi
        require_index "$2"
        show_test "$2"
        ;;
    run)
        shift
        timeout_arg=()
        log_arg=()
        while [ $# -gt 1 ]; do
            case "$1" in
                slow)
                    timeout_arg=(--ipc-timeout 0.3)
                    shift
                    ;;
                sloow)
                    timeout_arg=(--ipc-timeout 1)
                    shift
                    ;;
                log)
                    log_arg=(--show-log)
                    shift
                    ;;
                *)
                    break
                    ;;
            esac
        done

        if [ $# -ne 1 ]; then
            usage
            exit 1
        fi

        run_tests "$1" -- "${{timeout_arg[@]}}" "${{log_arg[@]}}"
        ;;
    *)
        usage
        exit 1
        ;;
esac
'''

    with open(script_path, 'w') as f:
        f.write(script)

    os.chmod(script_path, 0o755)
    return script_path

def run_test_once(args: argparse.Namespace, test_main_file, TestType, wayfire_exe, logfile: str, timeoutMultiplier: float, image_prefix: str, is_wayfire_B = False) -> TestResult:
    # Go to the directory of the test, so that any temporary files are stored there
    # and so that the wayfire.ini file can be found easily
    cwd = os.getcwd()
    os.chdir(get_test_base_dir(test_main_file))

    actual_log = '/dev/stdout' if args.show_log and not is_wayfire_B else logfile
    result = _run_test_once(args, TestType, wayfire_exe, actual_log, os.getcwd() + '/' + image_prefix, timeoutMultiplier)
    os.chdir(cwd)
    return result

class FailedTest:
    def __init__(self, prefix: str, gui: bool):
        self.prefix = prefix
        self.gui = gui

def run_single_test(args: argparse.Namespace, testMain: str, timeoutMultiplier: float) -> Tuple[wftest.Status, str | None]:
    spec = importlib.util.spec_from_file_location("main", testMain)
    assert spec is not None
    assert spec.loader is not None
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo) # type:ignore

    if foo.is_gui() and args.compare_with: # type: ignore
        resultA = run_test_once(args, testMain, foo.WTest, args.wayfire, 'wayfireA.log', timeoutMultiplier, 'wayfireA') # type: ignore
        if resultA.status != wftest.Status.OK:
            return resultA.status, 'wayfireA: ' + str(resultA.msg)

        resultB = run_test_once(args, testMain, foo.WTest, args.compare_with, 'wayfireB.log', timeoutMultiplier, 'wayfireB', is_wayfire_B=True) # type: ignore
        if resultB.status == wftest.Status.CRASHED:
            return wftest.Status.SKIPPED, 'wayfireB: ' + str(resultB.msg)
        if resultB.status != wftest.Status.OK:
            return resultB.status, 'wayfireB fails?: ' + str(resultB.msg)

        if len(resultA.file_list) != len(resultB.file_list):
            return wftest.Status.GUI_WRONG, 'Test returns different amount of images?' + \
                    str(resultA.file_list) + ' vs. ' + str(resultB.file_list)

        for (fileA, fileB) in zip(resultA.file_list, resultB.file_list):
            sensitivity = 20.0
            if getattr(foo, 'sensitivity', None):
                sensitivity = foo.sensitivity()

            code = wu.compare_images(fileA, fileB, fileA + '.delta.png', sensitivity)
            if code == wu.ImageDiff.SIZE_MISMATCH:
                return wftest.Status.GUI_WRONG, 'Screenshot sizes are different: ' + fileA + ' vs. ' + fileB
            elif code == wu.ImageDiff.DIFFERENT:
                return wftest.Status.GUI_WRONG, 'Screenshots are different: ' + fileA + ' vs. ' + fileB

        return wftest.Status.OK, None

    elif not foo.is_gui() or args.force_gui:
        result = run_test_once(args, testMain, foo.WTest, args.wayfire, 'wayfire.log', timeoutMultiplier, '') # type: ignore
        return result.status, result.msg
    else:
        return wftest.Status.SKIPPED, 'GUI test needs --compare-with'

tests_ok = 0
tests_wrong = 0
tests_skip = 0
failed_tests: List[FailedTest] = []

def shouldRunTest(test_main_file: str) -> bool:
    base_dir = get_test_base_dir(test_main_file)
    test_categories_file = base_dir + '/test_categories.txt'
    if args.categories:
        categories = args.categories.split(',')
        if os.path.exists(test_categories_file):
            with open(test_categories_file, 'r') as f:
                for line in f:
                    if line[:-1] in categories:
                        return True
        return False
    else:
        return True

def run_single_test_retry(args: argparse.Namespace, filename: str) -> Tuple[wftest.Status, str | None, int]:
    status = wftest.Status.SKIPPED
    explanation = "Retries <= 0?"
    for i in range(args.maxretries):
        status, explanation = run_single_test(args, filename, float(i+1))
        if status == wftest.Status.OK:
            return status, explanation, i+1

    return status, explanation, args.maxretries

exit_test = False

def run_test_from_path(args: argparse.Namespace, filename: str) -> Tuple[wftest.Status, str | None]:
    global exit_test
    if exit_test:
        return wftest.Status.SKIPPED, "Test cancelled"

    print("Running test " + colored(filename, 'blue') + " - ", end='')
    status, explanation, tryIdx = run_single_test_retry(args, filename)

    message, color = status.value
    tryColor = 'green' if status == wftest.Status.OK and tryIdx == 1 else 'magenta'

    print(colored(message, color, attrs=['bold']), end='')
    if explanation:
        print(f" ({explanation}, try #{colored(str(tryIdx), tryColor)})")
    else:
        print(f" (try #{colored(str(tryIdx), tryColor)})")

    return status, explanation

def run_all_tests(args: argparse.Namespace, ):
    print("Running tests in directory " + colored(args.testdir, "yellow"))
    test_list = []
    seen = set()

    if args.failscript_test:
        candidates = args.failscript_test
    else:
        candidates = glob.iglob(args.testdir + '/**/main.py', recursive=True)

    for filename in candidates:
        if filename in seen or not shouldRunTest(filename):
            continue

        seen.add(filename)
        test_list.append(filename)

    results_list = []

    with Pool(args.j) as pool:
        results_list = pool.starmap(run_test_from_path, [(args, test) for test in test_list])
        pool.close()

    # Calculate statistics
    global tests_ok
    global tests_wrong
    global tests_skip
    global failed_tests
    for (filename, (status, _)) in zip(test_list, results_list):
        if status == wftest.Status.OK:
            tests_ok += 1
        elif status == wftest.Status.SKIPPED:
            tests_skip += 1
        elif status == wftest.Status.WRONG or status == wftest.Status.CRASHED:
            tests_wrong += 1
            failed_tests.append(FailedTest(filename, False))
        else: # GUI_WRONG
            tests_wrong += 1
            failed_tests.append(FailedTest(filename, True))

def print_test_summary():
    # Print summary
    text_ok=colored(str(tests_ok) + " ok", 'green' if tests_wrong == 0 else 'blue', attrs=['bold'])
    text_wrong="0 not ok" if tests_wrong == 0 else colored(str(tests_wrong) + " not ok", 'red', attrs=['bold'])
    text_skipped="0 skipped" if tests_skip == 0 else colored(str(tests_skip) + " skipped", 'yellow', attrs=['bold'])
    print("Test summary: {} / {} / {}".format(text_ok, text_wrong, text_skipped))

def show_failed_tests():
    global failed_tests
    if not failed_tests:
        return

    print()
    print()
    print("Failed tests, enter number to see logs or image diffs:")
    for i, test in enumerate(failed_tests):
        print(colored(str(i) + '.', 'blue'),
                colored(get_test_base_dir(test.prefix), 'red'))

def merge_previous_failed_tests(args: argparse.Namespace):
    global failed_tests
    if not args.failscript_previous:
        return

    previous_failed = [decode_failed_test(raw) for raw in args.failscript_previous]
    current_by_prefix = {test.prefix: test for test in failed_tests}
    selected_dirs = {
        os.path.normpath(os.path.abspath(get_test_base_dir(path)))
        for path in args.failscript_test
    }
    merged: List[FailedTest] = []
    seen = set()

    for test in previous_failed:
        current = current_by_prefix.get(test.prefix)
        base_dir = os.path.normpath(os.path.abspath(get_test_base_dir(test.prefix)))

        if current:
            merged.append(current)
            seen.add(current.prefix)
        elif base_dir not in selected_dirs:
            merged.append(test)
            seen.add(test.prefix)

    for test in failed_tests:
        if test.prefix not in seen:
            merged.append(test)

    failed_tests = merged

def check_exec(path):
    if not os.access(path, os.X_OK):
        print("The given wayfire binary \"" + path + "\" is not executable!")
        sys.exit(-1)

def check_arguments():
    check_exec(args.wayfire)
    if args.compare_with:
        check_exec(args.compare_with)

if __name__ == "__main__":
    _args = parser.parse_args()
    args = _args
    check_arguments()

    try:
        assert args # type: ignore
        run_all_tests(args)
    except KeyboardInterrupt:
        exit_test = True
        print('Ctrl-C, stopping tests...')
        # Waiting for the background threads which kill all process groups
        print("Cleaning up...")
        time.sleep(1.0)
        sys.exit(0)

    tests_total = tests_ok + tests_skip + tests_wrong

    merge_previous_failed_tests(args)
    print_test_summary()
    if args.failscript:
        script_path = write_failscript(args)
        show_failed_tests()
        print(f"Updated {colored(script_path, 'yellow')} ({len(failed_tests)} failing tests recorded)")

    # Waiting for the background threads which kill all process groups
    print("Cleaning up...")
    time.sleep(1.0)
