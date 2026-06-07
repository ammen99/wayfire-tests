#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# Test for Wayfire #2077: pointer constraints in locked mode, with set cursor hint
# Idea is that cursor is first locked somewhere inside gtk_logger, and then after a click,
# it should warp to a client-defined position inside the surface.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        self.socket.move_cursor(500, 500) # Move out of the way of gtk1 so that pointer doesn't get immediately confined
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'lock-pointer')
        self.wait_for_clients(2)
        if len(self.socket.list_views()) != 1:
            return wt.Status.WRONG, 'Expected exactly one view, got: ' + str(self.socket.list_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 200, 200)
        self.socket.layout_views(layout)
        gtk1.reset_logs()
        self.wait_for_clients(2)

        self.socket.move_cursor(150, 150)
        self.wait_for_clients(2)
        if not gtk1.expect_line("pointer-enter"):
            return wt.Status.WRONG, 'gtk1 did not receive enter: ' + gtk1.last_line
        if not gtk1.expect_line("pointer-locked"):
            return wt.Status.WRONG, 'pointer was not locked! ' + gtk1.last_line

        self.socket.move_cursor(300, 300) # Outside of client, but should be confined to the corner
        self.socket.move_cursor(0, 0) # Outside of client, but should be confined to the corner
        self.wait_for_clients(2)

        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 got unexpected events when pointer was locked: ' + gtk1.last_line

        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients()
        if not gtk1.expect_line("button-press 272"):
            return wt.Status.WRONG, 'gtk1 did not receive button press: ' + gtk1.last_line
        if not gtk1.expect_line("button-release 272"):
            return wt.Status.WRONG, 'gtk1 did not receive button release: ' + gtk1.last_line

        pos = self.socket.sock.get_cursor_position()
        if pos != (15.0, 23.0):
            return wt.Status.WRONG, f'Cursor not warped to hint position (15, 23), got: {pos}'

        return wt.Status.OK, None
