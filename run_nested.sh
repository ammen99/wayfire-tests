#!/bin/zsh

# Kill children on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

WLR_RENDER_DRM_DEVICE=/dev/dri/renderD128 WLR_BACKENDS=headless wayfire -c miniconfig.ini &> /tmp/outerlog &
sleep 1
display=$(cat /tmp/outerlog | grep "Using socket name" | choose -1 | sed 's/.$//')

rm -rf $1/**/*.png
rm -rf $1/**/*.log
WAYLAND_DISPLAY=$display ./run_tests.sh "$@"