#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens a special gtk client and verifies that it receives pointer focus immediately after
# creation and before any simulated pointer input.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.move_cursor(110, 110) # Wayfire opens views with position 100, 100 initially
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has unexpected output: ' + gtk1.last_line

        return wt.Status.OK, None
