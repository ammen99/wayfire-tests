#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# wayfire #1927
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard &> /tmp/log')
        self.wait_for_clients_to_open(nr_clients=1)
        gtk1.reset_logs()

        # Make gcs always-on-top
        self.socket.press_key('KEY_T')

        # start scale, switch to gcs, exit by clicking on gcs
        self.socket.press_key('KEY_S')
        self.wait_for_clients()
        self.socket.move_cursor(250, 250) # middle of the screen
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        try:
            gtk1.expect_line_throw('keyboard-leave')
            gtk1.expect_line_throw('keyboard-enter')
            gtk1.expect_none_throw()
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
