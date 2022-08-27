#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-gamma-blend'])

    def _run(self):
        self.socket.run('wleird-gamma-blend')
        self.wait_for_clients()
        self.socket.press_key('KEY_I')
        self.wait_for_clients()

        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
