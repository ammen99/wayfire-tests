#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        try:
            gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard pointer')
            self.wait_for_clients(2)

            layout = {}
            layout['gtk1'] = (0, 0, 500, 500)
            self.socket.layout_views(layout)

            self.wait_for_clients(2)
            gtk1.reset_logs()

            # Go to workspace 2
            self.socket.press_key('KEY_2')
            self.wait_for_clients(2)
            gtk1.expect_unordered_lines_throw(['keyboard-leave', 'pointer-leave'])

            gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard pointer')
            self.wait_for_clients(2)

            layout = {}
            layout['gtk2'] = (0, 0, 500, 500)
            self.socket.layout_views(layout)
            self.wait_for_clients(2)
            gtk2.reset_logs()

            self.socket.press_key('KEY_1')
            self.wait_for_clients(2)
            gtk2.expect_unordered_lines_throw(['keyboard-leave', 'pointer-leave'])
            gtk1.expect_unordered_lines_throw(['keyboard-enter', 'pointer-enter'])

            gtk1.expect_none_throw()
            gtk2.expect_none_throw()
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
