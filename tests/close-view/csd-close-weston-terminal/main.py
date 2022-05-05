#!/bin/env python3

import wftest as wt
import wfipclib as wi
import shutil
import time

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('weston-terminal'):
            return wt.Status.SKIPPED, "weston-terminal binary not found in $PATH"
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('weston-terminal -m')
        time.sleep(0.1) # Wait for weston-terminal to start

        terminal = self.socket.get_view_info('nil')
        x = terminal['geometry']['x'] + terminal['geometry']['width'] - 16
        y = terminal['geometry']['y'] + 16
        self.socket.move_cursor(x, y)
        self.socket.click_button('BTN_LEFT', 'full')
        time.sleep(0.1) # Wait for weston-terminal to close

        if len(self.socket.list_views()) > 0:
            print(self.socket.list_views())
            return wt.Status.WRONG, "weston-terminal is still open"

        return wt.Status.OK, None
