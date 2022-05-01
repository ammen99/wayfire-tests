#!/bin/env python3

import wftest as wt
import traceback

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def run(self, wpath, log):
        try:
            self.run_wayfire(wpath, log)
            if self.socket.ping():
                return wt.Status.OK, "Test runner works :D"
            else:
                return wt.Status.WRONG, "Wayfire failed to respond to ping"

        except Exception as _:
            return wt.Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()
