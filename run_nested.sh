#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <test_directory>"
    exit 1
fi

# Kill children on exit
trap "trap - SIGTERM && pkill -P $$ && exit" SIGINT SIGTERM EXIT

export OLD_DISPLAY=$DISPLAY
export OLD_WAYLAND_DISPLAY=$WAYLAND_DISPLAY

unset DISPLAY
unset WAYLAND_DISPLAY

export WAYFIRE_BIN="${WAYFIRE_BIN:-wayfire}"
export DRM_DEVICE="${WLR_RENDER_DRM_DEVICE:-/dev/dri/renderD128}"
export OUTER_LOG="${OUTER_LOG:-/tmp/outerlog}"

WLR_RENDER_DRM_DEVICE=$DRM_DEVICE WLR_RENDERER=gles2 WLR_BACKENDS=headless $WAYFIRE_BIN -c miniconfig.ini &> $OUTER_LOG &
sleep 1
display=$(cat $OUTER_LOG | grep "Using socket name" | cut -d ' ' -f 9)

rm -rf $1/**/*.png
rm -rf $1/**/*.log
WAYLAND_DISPLAY=$display ./run_tests.sh "$@"
