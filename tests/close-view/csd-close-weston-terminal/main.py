#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('weston-terminal'):
            return wt.Status.SKIPPED, "weston-terminal binary not found in $PATH"
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh -m')
        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_for_clients(2) # for resize

        terminal = self.socket.get_view_info('nil')
        x = terminal['geometry']['x'] + terminal['geometry']['width'] - 16
        y = terminal['geometry']['y'] + 16
        self.socket.move_cursor(x, y)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        if len(self.socket.list_views()) > 0:
            return wt.Status.WRONG, "weston-terminal is still open"

        return wt.Status.OK, None
