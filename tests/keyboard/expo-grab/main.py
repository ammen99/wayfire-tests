#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens the gtk special client and uses it to open dialogs and then close them with
# simple keypresses. It also clicks a few times to attempt changing the focus, which should fail,
# as dialogs are always focused and not the main view.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients(10)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo app did not open: ' + str(self._get_views())

        try:
            gtk1.expect_line_throw("keyboard-enter")
            self.socket.press_key('S-KEY_E')
            self.wait_for_clients(2)

            gtk1.expect_line_throw("key-press 125", "(super mod)")
            gtk1.expect_line_throw("key-release 125", "(super mod)")
            gtk1.expect_line_throw("keyboard-leave")
            gtk1.expect_none_throw("after starting expo")

            self.socket.press_key('KEY_T')
            gtk1.expect_none_throw("during expo")

            self.socket.press_key('S-KEY_E')
            self.wait_for_clients(2)
            gtk1.expect_line_throw("keyboard-enter", "(after expo)")
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Did apps crash? ' + str(self._get_views())

        return wt.Status.OK, None
