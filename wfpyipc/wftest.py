import os

def _end_test(code):
    exit(os.getenv(code))

def ok():
    _end_test("WF_TEST_OK")

def wa():
    _end_test("WF_TEST_WRONG")

def crash():
    _end_test("WF_TEST_CRASH")

def skip():
    _end_test("WF_TEST_SKIP")

