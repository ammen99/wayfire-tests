#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# Wayfire 1919: press alt-esc, check that keyboard events are correct
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout['gtk1'] = (0, 0, 500, 500)
        layout['gtk2'] = (500, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Focus gtk1 on the left
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        gtk1.reset_logs()
        gtk2.reset_logs()

        try:
            self.socket.press_key('W-KEY_ESC')
            self.wait_for_clients(2)
            gtk1.expect_line_throw('key-press 125')
            gtk1.expect_line_throw('keyboard-leave')
            gtk1.expect_none_throw()

            gtk2.expect_line_throw('keyboard-enter')
            gtk2.expect_none_throw()
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
