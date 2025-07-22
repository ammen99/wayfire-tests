#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Test set/unset_maximized before first configure
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wayfire2744'])

    def _run(self):
        self.socket.run('wayfire2744')
        self.wait_ms(500)
        # It is ok as long as wayfire can survive this :)
        return wt.Status.OK, None
