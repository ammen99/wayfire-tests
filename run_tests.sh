#!/bin/sh

PYTHONPATH=$PYTHONPATH:$(pwd)/wfpytest/ ./run_tests.py "$@"
