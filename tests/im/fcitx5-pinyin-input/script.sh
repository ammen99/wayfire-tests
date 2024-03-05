#!/bin/sh

../fcitx-wrapper/start-fcitx5.sh &
WAYLAND_DEBUG=1 gedit &> /tmp/glog
