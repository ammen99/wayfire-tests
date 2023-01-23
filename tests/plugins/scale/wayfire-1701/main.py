#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Wayfire issue #1701
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        # Toggle scale once
        self.socket.press_key('KEY_S')
        self.wait_for_clients()
        self.socket.press_key('KEY_S')
        self.wait_for_clients()

        # Open a new window
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        # Type a bit => the scale title filter should not activate, neither should titles be shown
        self.socket.press_key('KEY_T')
        self.socket.press_key('KEY_H')
        self.socket.press_key('KEY_I')

        if error := self.take_screenshot('scale-does-not-show-anything'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
