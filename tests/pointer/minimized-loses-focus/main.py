#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# This test opens a gtk client and minimizes it. The client should then lose pointer focus.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo app did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(500, 500) # Move out of test clients
        gtk1.reset_logs()

        # Go to gtk1
        self.socket.move_cursor(50, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has unexpected output: ' + gtk1.last_line

        self.socket.press_key('KEY_M')
        self.wait_for_clients()
        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line

        self.socket.move_cursor(50, 60)
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output2: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'App crashed? ' + str(self._get_views())

        return wt.Status.OK, None
