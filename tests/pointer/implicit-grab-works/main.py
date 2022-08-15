
#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

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
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        layout['gtk2'] = (100, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(500, 500) # Move out of test clients
        gtk1.reset_logs()
        gtk2.reset_logs()

        # Go to gtk1 and start implicit grab
        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_line("button-press 272"): # 272 is BTN_LEFT
            return wt.Status.WRONG, 'gtk1 did not receive click: ' + gtk1.last_line

        # Move cursor inside gtk1
        self.socket.move_cursor(50, 60)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-motion 50,60"):
            return wt.Status.WRONG, 'gtk1 did not receive motion2: ' + gtk1.last_line

        # Move cursor to gtk2 => gtk1 should still get the events as it has implicit grab
        self.socket.move_cursor(100, 40)
        self.socket.move_cursor(150, 50)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-motion 100,40"):
            return wt.Status.WRONG, 'gtk1 did not receive motion3: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-motion 150,50"):
            return wt.Status.WRONG, 'gtk1 did not receive motion4: ' + gtk1.last_line
        if not gtk2.expect_none():
            return wt.Status.WRONG, 'gtk2 got some events despite implicit grab on gtk1! ' + gtk2.last_line

        # Release button => gtk2 should get focus
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)
        if not gtk1.expect_line("button-release 272"): # 272 is BTN_LEFT
            return wt.Status.WRONG, 'gtk1 did not receive button release: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line
        if not gtk2.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk2 did not receive enter: ' + gtk2.last_line
        if not gtk2.expect_none():
            return wt.Status.WRONG, 'gtk2 has trailing output: ' + gtk2.last_line

        if self._get_views() != ['gtk1', 'gtk2']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None

