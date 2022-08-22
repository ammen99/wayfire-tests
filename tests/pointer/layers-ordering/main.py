#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# This test opens a special gtk client twice, then proceeds to move the pointer to test that the correct
# client receives motion events
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'wleird-layer-shell'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        self.wait_for_clients(2)

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        self.socket.move_cursor(500, 500) # Move out of test client
        gtk1.reset_logs()

        # Go to gtk1
        self.socket.move_cursor(50, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line

        # Start background layer => focus should remain
        self.socket.run('wleird-layer-shell -l bottom -w 1280 -h 720 -c green')
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has unexpected output: ' + gtk1.last_line

        # Start top layer => focus should switch to new client
        self.socket.run('wleird-layer-shell -l top -w 1280 -h 720 -c red')
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line

        return wt.Status.OK, None
