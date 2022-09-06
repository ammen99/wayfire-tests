#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens a special gtk client which logs pointer events and opens a subsurface on click.
# It then proceeds to check that both the main surface and the subsurface receive correct events.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer click-to-menu')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (300, 300, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(350, 350) # middle of main surface
        self.socket.click_button('BTN_LEFT', 'full') # open subsurface
        self.wait_for_clients(2)
        gtk1.reset_logs()

        # Go to gtk1
        self.socket.move_cursor(310, 310)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-motion 10,10"):
            return wt.Status.WRONG, 'gtk1 main surface did not get correct motion: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has unexpected output: ' + gtk1.last_line

        self.socket.move_cursor(270, 350) # Somewhere in subsurface
        self.socket.move_cursor(270, 360) # Somewhere in subsurface
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-leave"): # Leave main surface
            return wt.Status.WRONG, 'gtk1 main surface did not get leave: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 subsurface did not get enter: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-motion 170,160"):
            return wt.Status.WRONG, 'gtk1 subsurface did not get correct motion: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
