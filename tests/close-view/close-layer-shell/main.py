#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['swaylock'])

    def _run(self):
        pid = self.socket.run('swaylock')["pid"]
        self.wait_for_clients(2)

        os.kill(pid, signal.SIGTERM)
        self.wait_for_clients(2)

        if len(self.socket.list_views()) > 0:
            print(self.socket.list_views())
            return wt.Status.WRONG, "swaylock is still open"

        return wt.Status.OK, None
