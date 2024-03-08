#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return wt.Status.OK, None

    def _run(self):
        self.socket.set_touch(1, 10, 10)
        self.socket.set_touch(1, 10, 20)
        return wt.Status.OK, None

