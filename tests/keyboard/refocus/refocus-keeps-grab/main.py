#!/bin/env python3

import wftest as wt
import wfutil as wu
import os
import signal

def is_gui() -> bool:
    return False

# This test opens the gtk special client and uses it to open dialogs and then close them with
# simple keypresses. It also clicks a few times to attempt changing the focus, which should fail,
# as dialogs are always focused and not the main view.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'wleird-layer-shell'])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients(2)
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients(2)

        if not gtk1.expect_line("keyboard-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_line("keyboard-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line
        if not gtk2.expect_line("keyboard-enter"):
            return wt.Status.WRONG, 'gtk2 did not receive enter: ' + gtk2.last_line

        self.socket.run('wleird-layer-shell -l top -k exclusive -c green')
        self.wait_for_clients(2)
        if not gtk2.expect_line("keyboard-leave"):
            return wt.Status.WRONG, 'gtk2 did not receive leave: ' + gtk2.last_line

        os.kill(gtk1.pid, signal.SIGINT)
        self.wait_for_clients(2)

        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output receive leave: ' + gtk1.last_line

        return wt.Status.OK, None
