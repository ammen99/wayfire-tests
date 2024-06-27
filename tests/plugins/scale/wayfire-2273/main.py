#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('python3 client.py')
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_ms(500)

        for _ in range(4):
            self.socket.press_key('KEY_S')
            self.wait_for_clients(2)

        self.wait_ms(150)

        # Hope that ping is OK
        return wt.Status.OK, None
