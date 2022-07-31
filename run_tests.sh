#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Build clients first
(
cd $SCRIPT_DIR/clients
if ! [ -d build/ ]; then
    meson build
fi
ninja -C build
)

PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/wfpytest/ PATH=$PATH:$SCRIPT_DIR/clients/build $SCRIPT_DIR/run_tests.py "$@"
