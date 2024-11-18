#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-layer-shell'])

    def _run(self):
        pid = self.socket.run('wleird-layer-shell -l top')["pid"]
        self.wait_for_clients(2)

        self.send_signal(pid, signal.SIGKILL)
        self.wait_ms(150) # Wait for animation to end

        if len(self.socket.list_views()) > 0:
            return wt.Status.WRONG, "swaylock is still open"

        return wt.Status.OK, None
