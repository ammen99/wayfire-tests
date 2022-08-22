
#!/bin/env python3

import wfipclib as wi
import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# Test that during pinch in 3, the fingers are released when expo is activated
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'touch')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Put down the 3 fingers for pinch in
        self.socket.set_touch(0, 10, 10)
        self.socket.set_touch(1, 90, 15)
        self.socket.set_touch(2, 46, 87)

        # Pinch-in
        self.socket.set_touch(0, 45, 35)
        self.socket.set_touch(1, 50, 33)
        self.socket.set_touch(2, 49, 40)

        self.wait_for_clients(2)

        if not gtk1.expect_line("touch-down 0 10 10"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-down 0: ' + gtk1.last_line
        if not gtk1.expect_line("touch-down 1 90 15"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-down 1: ' + gtk1.last_line
        if not gtk1.expect_line("touch-down 2 46 87"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-down 2: ' + gtk1.last_line

        if not gtk1.expect_line("touch-motion 0 45 35"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-motion 0: ' + gtk1.last_line
        if not gtk1.expect_line("touch-motion 1 50 33"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-motion 1: ' + gtk1.last_line

        if not gtk1.expect_line("touch-up 0"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-up 0: ' + gtk1.last_line
        if not gtk1.expect_line("touch-up 1"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-up 1: ' + gtk1.last_line
        if not gtk1.expect_line("touch-up 2"):
            return wt.Status.WRONG, 'gtk1 did not receive touch-up 2: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
