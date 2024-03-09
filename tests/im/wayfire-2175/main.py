#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        self.socket.press_key('KEY_E')
        self.wait_for_clients(1) # wait for expo
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard text-input')
        self.wait_for_clients_to_open(nr_clients=1)
        return wt.Status.OK, None
