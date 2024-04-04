#!/bin/env python3

import wftest as wt
from time import sleep


def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def _run(self):
        # the goal of this code is to run the fuzz test not to make it fit wayfire-tests code of conduct
        # the code will hang until the timeout ends
        self.socket.create_wayland_output()
        self.socket.run("kitty --hold -- sh fuzz.sh")
        timeout = 7
        sleep(timeout)
        return wt.Status.OK, None
