#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-layer-shell'])

    def _run(self):
        pid = self.socket.run('wleird-layer-shell')['pid']
        self.wait_for_clients()

        self.send_signal(pid, signal.SIGINT)
        self.wait_ms(200)

        if len(self.socket.list_views()) > 0:
            return wt.Status.WRONG, "wleird-layer-shell is still open"

        return wt.Status.OK, None
