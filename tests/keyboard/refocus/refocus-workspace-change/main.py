#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# This test opens gtk_logger twice, on workspaces 1 and 2.
# It then checks that when switching workspaces, the focus is changed correctly.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients(2)
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients(2)
        def expect_no_trailing():
            for gtk in [gtk1, gtk2]:
                if not gtk.expect_none():
                    return wt.Status.WRONG, 'gtk2/3 has trailing output: ' + gtk.last_line
            return None

        layout = {}
        layout['gtk1'] = (400, 400, 100, 100) # Workspace 1
        layout['gtk2'] = (500, 0, 100, 100) # Workspace 2
        self.socket.layout_views(layout)
        self._click_on(self.socket.get_view_info_title('gtk1'))
        self.wait_for_clients(2)
        gtk1.reset_logs()
        gtk2.reset_logs()
        if err := expect_no_trailing():
            return err

        self.socket.press_key('KEY_B') # Workspace 2

        self.wait_for_clients(2)
        if not gtk1.expect_line("keyboard-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line
        if not gtk2.expect_line("keyboard-enter"):
            return wt.Status.WRONG, 'gtk2 did not receive enter: ' + gtk2.last_line
        if err := expect_no_trailing():
            return err

        self.socket.press_key('KEY_C') # Workspace 3
        self.wait_for_clients()
        if not gtk2.expect_line("keyboard-leave"):
            return wt.Status.WRONG, 'gtk2 did not receive leave: ' + gtk2.last_line
        if err := expect_no_trailing():
            return err

        return wt.Status.OK, None
