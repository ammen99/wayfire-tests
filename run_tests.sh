#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

(
cd $SCRIPT_DIR
git submodule update --init
)

# Build clients first

function build_dir {
    (
    cd $SCRIPT_DIR/$1
    if ! [ -d build/ ]; then
        meson build
    fi
    ninja -C build
    )
}

build_dir clients
build_dir wleird

WF_TEST_LAUNCHER="${WF_TEST_LAUNCHER:-$SCRIPT_DIR/run_tests.sh}" PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/wfpytest/ PATH=$PATH:$SCRIPT_DIR/clients/build:$SCRIPT_DIR/wleird/build $SCRIPT_DIR/run_tests.py "$@"
