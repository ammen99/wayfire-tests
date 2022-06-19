#!/bin/sh

PYTHONPATH=$PYTHONPATH:$(pwd)/wfpytest/ PATH=$PATH:$(pwd)/clients ./run_tests.py "$@" 
