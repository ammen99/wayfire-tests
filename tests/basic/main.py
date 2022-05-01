#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def _run(self):
        return wt.Status.OK, None
