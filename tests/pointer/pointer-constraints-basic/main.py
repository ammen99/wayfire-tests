#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens a special gtk client which confines the pointer to itself with the pointer-constraints protocol.
# Then it proceeds to check that:
# 1) Once pointer enters, it does not leave the surface when moved out.
# 2) A plugin (expo) can break the constraint
# 3) Constraint can be reactivated
# 4) There is no crash when closing the view while constraint is active
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.move_cursor(500, 500) # Move out of the way of gtk1 so that pointer doesn't get immediately confined
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer confine click-to-close')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'gtk_logger did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (100, 100, 100, 100)
        self.socket.layout_views(layout)
        gtk1.reset_logs()
        # FIXME: Workaround wayfire bug - confined region does not change on surface commit,
        # so we have to wait until wl_surface.commit happens to trigger the confinement with
        # the correct region AFTER gtk1 is resized.
        self.wait_for_clients(2)

        self.socket.move_cursor(150, 150)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-confined"):
            return wt.Status.WRONG, 'pointer was not confined the first time! ' + gtk1.last_line

        self.socket.move_cursor(300, 300) # Outside of client, but should be confined to the corner
        self.socket.move_cursor(0, 0) # Outside of client, but should be confined to the corner
        self.wait_for_clients(2)

        if not gtk1.expect_line("pointer-motion 99,99"):
            return wt.Status.WRONG, 'pointer not properly confined to bottom-right corner: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-motion 0,0"):
            return wt.Status.WRONG, 'pointer not properly confined to top-left corner: ' + gtk1.last_line

        self.socket.press_key('KEY_E') # Expo should break it
        self.wait_for_clients(2)

        if not gtk1.expect_line("pointer-leave"):
            return wt.Status.WRONG, 'gtk1 did not receive leave when expo starts: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-unconfined"):
            return wt.Status.WRONG, 'pointer was not unconfined when expo starts: ' + gtk1.last_line

        self.socket.move_cursor(300, 300) # Outside of client
        self.socket.press_key('KEY_E') # Close expo => we expect no confinement
        self.wait_for_clients(2)

        if not gtk1.expect_none():
            return wt.Status.WRONG, 'Extra output after closing expo: ' + gtk1.last_line

        self.socket.move_cursor(150, 150) # Middle of client
        self.socket.click_button('BTN_LEFT', 'press') # Close with click-to-close
        self.wait_for_clients(2) # Wait for gtk to process the last event and close
        self.socket.click_button('BTN_LEFT', 'release')
        self.socket.move_cursor(250, 150) # Motion should not crash wayfire, but should not be sent to the client
        self.wait_for_clients(2)

        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter after Expo: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-confined"):
            return wt.Status.WRONG, 'pointer was not confined the second time time! ' + gtk1.last_line
        if not gtk1.expect_line("button-press 272"):
            return wt.Status.WRONG, 'gtk1 did not get button press: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output in the end of test: ' + gtk1.last_line

        if self._get_views() != []:
            return wt.Status.WRONG, 'gtk_logger did not open: ' + str(self._get_views())

        if not self.socket.ping():
            return wt.Status.WRONG, 'Wayfire crashed at some point?'

        return wt.Status.OK, None
