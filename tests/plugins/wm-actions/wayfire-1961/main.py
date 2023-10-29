#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire 1961: try to toggle always_on_top with no views
class WTest(wt.WayfireTest):
    def prepare(self):
        return wt.Status.OK, None

    def _run(self):
        self.socket.press_key('KEY_T')
        if not self.socket.ping():
            return wt.Status.WRONG, "Wayfire died?"

        return wt.Status.OK, None
