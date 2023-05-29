#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# This test opens gtk-logger and sends it back and forth between outputs and workspace sets
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        try:
            self.socket.create_wayland_output()
            self.socket.move_cursor(250, 250)
            self.socket.click_button('BTN_LEFT', 'full') # Ensure focus on WL-1

            gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
            self.wait_for_clients(2)

            layout = {}
            layout['gtk1'] = (100, 100, 300, 300)
            self.socket.layout_views(layout)
            self.wait_for_clients(2)

            gtk1.reset_logs()

            # Send to wset 2 on WL-2
            self.socket.press_key('KEY_B')
            self.wait_for_clients(2)
            gtk1.expect_unordered_lines_throw(['keyboard-leave'])

            # Focus WL-2
            self.socket.move_cursor(750, 250)
            self.socket.click_button('BTN_LEFT', 'full') # Ensure focus on WL-1
            self.wait_for_clients(2)
            gtk1.expect_unordered_lines_throw(['keyboard-enter'])

            # Send to wset 3 (no output)
            self.socket.press_key('KEY_C')
            self.wait_for_clients(2)
            gtk1.expect_unordered_lines_throw(['keyboard-leave'])

            # Go to wset 3
            self.socket.press_key('KEY_3')
            self.wait_for_clients(2)
            gtk1.expect_unordered_lines_throw(['keyboard-enter'])
            gtk1.expect_none_throw()
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
