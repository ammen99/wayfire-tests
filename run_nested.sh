#!/bin/zsh

# Kill children on exit
trap "trap - SIGTERM && pkill -P $$ && exit" SIGINT SIGTERM EXIT

unset DISPLAY
unset WAYLAND_DISPLAY

WLR_RENDERER=gles2 WLR_RENDER_DRM_DEVICE=/dev/dri/renderD128 WLR_BACKENDS=headless wayfire -c miniconfig.ini &> /tmp/outerlog &
sleep 1
display=$(cat /tmp/outerlog | grep "Using socket name" | cut -d ' ' -f 9)

rm -rf $1/**/*.png
rm -rf $1/**/*.log
WAYLAND_DISPLAY=$display ./run_tests.sh "$@"
