
#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test opens a special gtk client twice, then proceeds to move the pointer to test that the correct
# client receives motion events
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(500, 500) # Move out of test clients
        gtk1.reset_logs()

        # Go to gtk1 and start implicit grab
        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_line("button-press 272"): # 272 is BTN_LEFT
            return wt.Status.WRONG, 'gtk1 did not receive click: ' + gtk1.last_line

        # Start expo => implicit grab should be broken (pointer_release + leave)
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if not gtk1.expect_line("button-release 272"):
            return wt.Status.WRONG, 'gtk1 did not receive button release: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive pointer leave: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line

        # Leave expo => client should get focus, but not any pointer event
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter2: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output2: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
