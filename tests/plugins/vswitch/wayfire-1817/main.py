#!/bin/env python3

import wftest as wt
from wfutil import LoggedProcess

def is_gui() -> bool:
    return False

# Wayfire #1817: with_win_* keeps focus
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk = LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=1)
        gtk.reset_logs()
        self.socket.press_key('KEY_R')
        self.wait_for_clients(2)

        try:
            gtk.expect_line_throw("keyboard-leave")
            gtk.expect_line_throw("keyboard-enter")
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
