#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# This test starts two clients on two different outputs.
# It then proceeds to check that the active output (one last clicked on) receives
# the predefined keybindings for closing a view, and the other output does not.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_logger'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        # Create WL-2
        self.socket.create_wayland_output()

        # Click and focus on WL-1
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')

        # Start keylogger
        x11 = wu.LoggedProcess(self.socket, 'x11_logger', 'x11', '&> /tmp/log')

        self.wait_for_clients(2)
        if self._get_views() != ['x11']:
            return wt.Status.WRONG, 'x11_logger did not open: ' + str(self._get_views())

        try:
            x11.expect_line_throw('focus-in')
            self.socket.press_key('KEY_T')
            self.wait_for_clients(2)
            x11.expect_line_throw('key-press 28')
            x11.expect_line_throw('key-release 28')
            x11.expect_none_throw('after initial key press')

            # Move to WL-2, click on x11
            self.socket.press_key('KEY_N')
            self.wait_for_clients(2)
            x11.expect_line_throw('focus-out', 'focus-out on oswitch')
            x11.expect_line_throw('focus-in', 'on new output')
            x11.expect_none_throw('after oswitch')

            self.socket.press_key('KEY_Y')
            self.wait_for_clients(2)
            x11.expect_line_throw('key-press 29')
            x11.expect_line_throw('key-release 29')
            x11.expect_none_throw('at the end')
        except Exception as e:
            return wt.Status.WRONG, 'Failed to get input: ' + str(e)

        return wt.Status.OK, None
