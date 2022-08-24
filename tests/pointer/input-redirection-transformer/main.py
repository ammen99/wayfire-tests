#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens the gtk_logger test client, rotates it 90 degrees ccw with wrot
# and proceeds to test that input redirection works as expected.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _move_expect(self, gtk1, x, y, expect_x, expect_y):
        self.socket.move_cursor(x, y)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-motion {}, {}".format(expect_x, expect_y)):
            return False
        return True

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(0, 0) # Move out of test clients
        self.socket.click_button('BTN_RIGHT', 'press')
        self.socket.move_cursor(0, 100) # Rotate 90 ccw
        self.socket.click_button('BTN_RIGHT', 'release')

        self.wait_for_clients(2)
        gtk1.reset_logs()

        # Go to gtk1
        if self._move_expect(gtk1, 50, 50, expect_x=50, expect_y=50):
            return wt.Status.WRONG, 'gtk1 did not receive motion to 50,50: ' + gtk1.last_line
        if self._move_expect(gtk1, 0, 0, expect_x=100, expect_y=0):
            return wt.Status.WRONG, 'gtk1 did not receive motion to 100,0: ' + gtk1.last_line
        if self._move_expect(gtk1, 80, 90, expect_x=10, expect_y=80):
            return wt.Status.WRONG, 'gtk1 did not receive motion to 10,80: ' + gtk1.last_line

        return wt.Status.OK, None
