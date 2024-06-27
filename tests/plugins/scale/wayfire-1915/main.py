#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# Wayfire 1915: filter out all views, press ESC
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=1)
        gtk.reset_logs()

        try:
            self.socket.press_key('KEY_S')
            self.wait_for_clients(2)
            gtk.expect_line_throw('keyboard-leave', 'when scale starts')
            gtk.expect_none_throw('when scale starts')
            for x in "XAZAJKDOAUDOAN": # garbage filter, just make sure not to press S again
                self.socket.press_key(f'KEY_{x}')

            self.wait_for_clients()
            gtk.expect_none_throw('after filter')
            self.socket.press_key('KEY_ESC')
            self.wait_for_clients()
            gtk.expect_line_throw('keyboard-enter', 'when scale exits')
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
