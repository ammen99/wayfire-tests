#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens three special clients which all overlap in the same area ((50, 50) to (100, 100))
# They are focused one by one by clicking on them.
# Then, they are closed one by one by right clicking on them.
# The order in which they are closed needs to reflect the stacking order created
# by the left clicks.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('x11_click_to_close'):
            return wt.Status.SKIPPED, "Did you compile test clients?"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('x11_click_to_close 1 0 0 100 100')
        self.socket.run('x11_click_to_close 2 50 50 100 100')
        self.socket.run('x11_click_to_close 3 0 50 100 100')
        self.wait_for_clients()

        # Bring 3 to front
        self.socket.move_cursor(1, 140)
        self.socket.click_button('BTN_LEFT', 'full')

        # Bring 1 to front
        self.socket.move_cursor(1, 1)
        self.socket.click_button('BTN_LEFT', 'full')

        # Bring 2 to front
        self.socket.move_cursor(140, 140)
        self.socket.click_button('BTN_LEFT', 'full')

        # Close windows one by one by clicking on the shared area
        if self._get_views() != ['1', '2', '3']:
            return wt.Status.WRONG, \
                'Could not find all three clients after test setup: ' + str(self._get_views())

        # Close 2
        self.socket.move_cursor(75, 75)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()
        if self._get_views() != ['1', '3']:
            return wt.Status.WRONG, 'Client 2 did not receive input ' + str(self._get_views())

        # Close 1
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()
        if self._get_views() != ['3']:
            return wt.Status.WRONG, 'Client 1 did not receive input ' + str(self._get_views())

        # Close 3
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()
        if self._get_views() != []:
            return wt.Status.WRONG, 'Client 3 did not receive input ' + str(self._get_views())

        return wt.Status.OK, None
