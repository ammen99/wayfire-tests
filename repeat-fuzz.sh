#!/bin/bash

counter=0
rm -rf stress-test.log
touch stress-test.log
rm /tmp/seeds

while [ $counter -lt 100 ]; do
    ((counter++))
    UBSAN_OPTIONS=print_stacktrace=true ./my_run.sh staging/fuzz-test /usr/bin/wayfire

    # Check if the log file contains the error string
    #if grep -q "shutting down" staging/fuzz-test/wayfire.log; then
    #    echo "Ignoring shutdown crash"
    #if grep -q "ERROR: AddressSanitizer:" staging/fuzz-test/wayfire.log; then
    if grep -q "runtime error" staging/fuzz-test/wayfire.log; then
        # Append the log file to stress-test.log
        cat staging/fuzz-test/wayfire.log >> stress-test.log
        exit 0
    fi
done
