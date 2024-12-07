#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Start scale, check that keyboard keys actually work
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['xdg_popup_crasher'])

    def _run(self):
        self.socket.run('xdg_popup_crasher -a')
        self.wait_for_clients(10)

        return wt.Status.OK, None
