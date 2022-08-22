
#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'touch')
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'touch')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        layout['gtk2'] = (100, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Go to gtk1 and start implicit grab
        self.socket.set_touch(0, 50, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_line("touch-down 0 50 50"):
            return wt.Status.WRONG, 'gtk1 did not receive touch down: ' + gtk1.last_line

        # Move cursor outside gtk1 while holding grab over gtk1
        self.socket.set_touch(0, 90, 50)
        self.socket.set_touch(0, 150, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_line("touch-motion 0 90 50"):
            return wt.Status.WRONG, 'gtk1 did not receive touch motion1: ' + gtk1.last_line
        if not gtk1.expect_line("touch-motion 0 150 50"):
            return wt.Status.WRONG, 'gtk1 did not receive touch motion2: ' + gtk1.last_line
        if not gtk2.expect_none():
            return wt.Status.WRONG, 'gtk2 received events!: ' + gtk2.last_line

        # Move cursor to gtk2
        self.socket.set_touch(1, 150, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line
        if not gtk2.expect_line("touch-down 1 50 50"):
            return wt.Status.WRONG, 'gtk2 did not receive second touch down: ' + gtk2.last_line

        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None

