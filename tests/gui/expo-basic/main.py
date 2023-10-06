#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-cursor', 'wleird-gamma-blend', 'wleird-layer-shell', 'gtk_color_switcher'])

    def _run(self):
        self.socket.run('wleird-layer-shell -l bottom -a bottom -w 500 -h 500 -c green')
        self.socket.run('wleird-layer-shell -l top -a left -c blue')
        self.socket.run('wleird-layer-shell -l top -a right -c red')
        self.socket.run('wleird-gamma-blend')
        self.socket.run('wleird-cursor')
        pid = self.socket.run('gtk_color_switcher cs')["pid"]
        self.wait_for_clients(2) # Wait for cursor to start

        layout = {}
        layout['wleird-gamma-blend'] = (0, 0, 400, 400)
        layout['cs'] = (2100, 50, 500, 400)
        layout['wleird-cursor'] = (1200, 530, 100, 100)
        self.socket.layout_views(layout)
        self.socket.press_key('KEY_4')
        self.wait_for_clients(1) # Wait for vswitch to exit
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2) # Wait for expo to start
        if error := self.take_screenshot('expo-start'):
            return wt.Status.CRASHED, error

        self.send_signal(pid, signal.SIGUSR1);
        self.wait_for_clients(2) # Wait for color-switcher to change color
        if error := self.take_screenshot('expo-damage'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
