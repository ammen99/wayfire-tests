#!/bin/bash

mkdir -p /tmp/replicated-tests/
rm -rf /tmp/replicated-tests/*
for i in $(seq 1 100); do
    cp $1 /tmp/replicated-tests/test-$i -r
done

shift 1
./run_nested.sh /tmp/replicated-tests "$@"
