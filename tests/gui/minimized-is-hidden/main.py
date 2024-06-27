#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2)

        self.socket.press_key('KEY_M')
        self.wait_for_clients()

        if error := self.take_screenshot('minimized-hidden'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
