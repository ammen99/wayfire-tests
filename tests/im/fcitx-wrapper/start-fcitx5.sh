#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export XDG_CONFIG_HOME=$SCRIPT_DIR
export FCITX_CONFIG_HOME=$SCRIPT_DIR/fcitx5
fcitx5
