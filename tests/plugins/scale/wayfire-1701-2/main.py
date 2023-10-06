#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return True

# Wayfire issue #1701
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        pid = self.socket.run('weston-terminal')['pid']
        self.wait_for_clients(2)

        # Toggle scale once
        self.socket.press_key('KEY_S')
        self.wait_for_clients()

        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(10)

        # Open a new window
        self.socket.run('weston-terminal')
        self.wait_for_clients(10)

        if error := self.take_screenshot('scale-does-not-show-anything'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
