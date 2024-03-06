#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export XDG_CONFIG_HOME=$SCRIPT_DIR
export FCITX_CONFIG_HOME=$SCRIPT_DIR/fcitx5
export DBUS_SESSION_BUS_ADDRESS=/dev/null
export IBUS_ADDRESS=/dev/null
fcitx5
