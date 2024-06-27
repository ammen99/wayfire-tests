#!/bin/env python3

import wfutil as wu
import wftest as wt

def is_gui() -> bool:
    return False

# Check that openarena (a Xwayland game) can use pointer constraints in a multi-output scenario
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'openarena'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('openarena')
        self.wait_for_clients_to_open(1)

        # Skip the 'abnormal start' button
        self.socket.press_key('KEY_ENTER')

        self.socket.create_wayland_output()
        self.socket.move_cursor(0, 0) # Move out of the way of gtk1 so that pointer doesn't get immediately confined
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer')
        self.wait_ms(1500) # Wait for the game to initialize properly
        if self._get_views() != ['gtk1', 'ioquake3']:
            return wt.Status.WRONG, 'Clients did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 500, 500, 'WL-2')
        layout['ioquake3'] = (0, 0, 500, 500, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        gtk1.reset_logs()
        self.wait_for_clients(2)

        self.socket.move_cursor(150, 150)
        self.socket.click_button('BTN_LEFT', 'full') # Trigger confinement to openarena
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'extra events when triggering confinement ' + gtk1.last_line

        self.socket.move_cursor(300, 300)
        self.socket.move_cursor(700, 200) # Outside of client, on WL-2
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'extra events after motion ' + gtk1.last_line

        self.socket.click_button('BTN_LEFT', 'full') # Trigger confinement to openarena
        self.socket.move_cursor(800, 300)
        self.wait_for_clients(2)
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'extra events when clicking on other output ' + gtk1.last_line

        return wt.Status.OK, None
