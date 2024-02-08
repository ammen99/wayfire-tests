#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=1)

        try:
            gtk1.expect_line_throw("keyboard-enter")
            self.socket.press_key('KEY_LEFTMETA')
            self.wait_for_clients(2)

            gtk1.expect_line_throw("key-press 125", "(super mod)")
            gtk1.expect_line_throw("keyboard-leave")
            gtk1.expect_none_throw("after starting expo")

            self.socket.press_key('KEY_LEFTMETA')
            self.wait_for_clients(2)

            gtk1.expect_line_throw("keyboard-enter", "(after expo)")
            gtk1.expect_none_throw("(after expo)")
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
