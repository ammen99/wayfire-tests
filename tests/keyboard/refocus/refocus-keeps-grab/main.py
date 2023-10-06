#!/bin/env python3

import wftest as wt
import wfutil as wu
import os
import signal

def is_gui() -> bool:
    return False

# This test opens gtk_logger twice, and a layer-shell surface with exclusive focus.
# It proceeds to check that the exclusive focus is correctly handled when the refocus
# operation is triggered, or when an attempt to focus a normal view is made.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'wleird-layer-shell'])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

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

        self.socket.run('wleird-layer-shell -l top -k exclusive -c green -a top -a right')
        self.wait_for_clients(2)
        if not gtk2.expect_line("keyboard-leave"):
            return wt.Status.WRONG, 'gtk2 did not receive leave: ' + gtk2.last_line

        self.send_signal(gtk2.pid, signal.SIGINT)
        self.wait_for_clients(2)

        self._click_on(self.socket.get_view_info_title('gtk1'))
        self.wait_for_clients(2)

        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output receive leave: ' + gtk1.last_line

        return wt.Status.OK, None
