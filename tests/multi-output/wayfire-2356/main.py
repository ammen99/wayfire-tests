#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wlopm'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('wlopm --off "*"')
        self.wait_for_clients(2)
        self.socket.run('wlopm --on "*"')
        self.wait_for_clients(2)

        if not self.socket.ping():
            return wt.Status.CRASHED, 'Wayfire crashed after enabling?'

        return wt.Status.OK, None
