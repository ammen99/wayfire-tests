#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['fcitx5', 'wl-paste', 'weston-terminal', 'gtk_logger'])

    def _run(self):
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard text-input')

        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_for_clients(2) # wait for im

        try:
            gtk1.expect_line_throw('keyboard-enter')
            self.socket.press_key('KEY_F')
            self.wait_for_clients()
            gtk1.expect_line_throw('key-release 33') # press is sent via text-input-v3
            self.socket.press_key('KEY_SPACE')
            self.wait_for_clients()
            gtk1.expect_line_throw('key-release 57') # press is sent via text-input-v3

            self.socket.press_key('S-KEY_ENTER')
            self.wait_for_clients_to_open(nr_clients=2)
            gtk1.expect_line_throw('key-press 125')
            gtk1.expect_line_throw('key-release 125')
            gtk1.expect_line_throw('keyboard-leave')
            gtk1.expect_none_throw()
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
