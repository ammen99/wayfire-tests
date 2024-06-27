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
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(4)
        self.socket.press_key('KEY_Q')
        self.wait_for_clients(2)

        if len(self.socket.list_views()) > 0:
            print(self.socket.list_views())
            return wt.Status.WRONG, "weston-terminal is still open"

        return wt.Status.OK, None
