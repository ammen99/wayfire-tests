#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test opens a special gtk client twice on different outputs so that they overlap.
# Then, it proceeds to check that despite the overlap, the correct view is focused every time,
# i.e. it checks that a view's input region is confined to its output.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'pointer')
        self.socket.create_wayland_output()
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (250, 0, 500, 500, 'WL-1') # Overlaps the left half of WL-2
        layout['gtk2'] = (0, 0, 100, 100, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(999, 499) # Move out of test clients, bottom-right of WL-2
        self.socket.click_button('BTN_LEFT', 'full') # Focus WL-2
        self.wait_for_clients(2) # Wait for messages to be flushed
        gtk1.reset_logs()
        gtk2.reset_logs()

        # Go to gtk1
        self.socket.move_cursor(450, 50) # Top-right of WL-1, on gtk1
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has unexpected output: ' + gtk1.last_line

        self.socket.click_button('BTN_LEFT', 'full') # Make sure WL-1 is focused
        self.wait_for_clients(2)
        if not gtk1.expect_line("button-press 272"):
            return wt.Status.WRONG, 'gtk1 did not receive button press: ' + gtk1.last_line
        if not gtk1.expect_line("button-release 272"):
            return wt.Status.WRONG, 'gtk1 did not receive button release: ' + gtk1.last_line

        self.socket.move_cursor(550, 50) # Move on WL-2 and focus gtk2
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line
        if not gtk2.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk2 did not receive enter: ' + gtk2.last_line

        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
