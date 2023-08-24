#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1695
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.press_key('KEY_R')
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_S')
        self.socket.press_key('KEY_R')
        return wt.Status.OK, None