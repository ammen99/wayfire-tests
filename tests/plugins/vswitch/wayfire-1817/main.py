#!/bin/env python3

import wftest as wt
from wfutil import LoggedProcess

def is_gui() -> bool:
    return False

# Wayfire #1817: with_win_* keeps focus
# Wayfire #1916: active view is kept when moving across workspaces
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk1 = LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        gtk2 = LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout['gtk1'] = (0, 0, 300, 300) # on workspace 1
        layout['gtk2'] = (600, 600, 300, 300) # on workspace 2
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # click gtk1 to ensure it is focused
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients()

        gtk1.reset_logs()
        gtk2.reset_logs()

        self.socket.press_key('KEY_R')
        self.socket.press_key('KEY_R')
        self.wait_ms(300)

        try:
            gtk1.expect_none_throw()
            gtk2.expect_none_throw()
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
