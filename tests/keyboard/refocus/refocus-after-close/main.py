#!/bin/env python3

import wftest as wt
import wfutil as wu
import signal

def is_gui() -> bool:
    return False

# This test opens gtk_logger twice, and proceeds to check that when a view is
# closed, windows which are barely visible on the current workspace are not focused in favor
# of windows which are more fully visible.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients(2)
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients(2)
        gtk3 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk3', 'keyboard')
        self.wait_for_clients(2)

        for gtk in [gtk1, gtk2]:
            if not gtk.expect_line("keyboard-enter"):
                return wt.Status.WRONG, 'gtk1/2 did not receive enter: ' + gtk.last_line
            if not gtk.expect_line("keyboard-leave"):
                return wt.Status.WRONG, 'gtk1/2 did not receive leave: ' + gtk.last_line
        if not gtk3.expect_line("keyboard-enter"):
            return wt.Status.WRONG, 'gtk3 did not receive enter: ' + gtk3.last_line

        layout = {}
        layout['gtk2'] = (495, 495, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.send_signal(gtk3.pid, signal.SIGKILL)
        self.wait_for_clients(2)
        if not gtk1.expect_line("keyboard-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive second enter: ' + gtk1.last_line
        for gtk in [gtk2, gtk3]:
            if not gtk.expect_none():
                return wt.Status.WRONG, 'gtk2/3 has trailing output: ' + gtk.last_line

        return wt.Status.OK, None
