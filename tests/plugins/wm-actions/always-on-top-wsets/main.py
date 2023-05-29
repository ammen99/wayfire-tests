#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return True

# This test activates the second workspace set and ensures that always-on-top state works as intended.
# Then it goes back to the first workspace and checks that always-on-top is hidden, and then shown again.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher', 'gtk_special'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        # Rotate through multiple workspace sets, trying to reorder them
        for x in [1, 2, 3, 2, 1, 3, 1, 3, 2]:
            self.socket.press_key('KEY_' + str(x))

        pid = self.socket.run('gtk_color_switcher')['pid']
        self.socket.run('gtk_special a')
        self.wait_for_clients(2)
        os.kill(pid, signal.SIGUSR1)
        if self._get_views() != ['gtk_color_switcher', 'gtk_special']:
            return wt.Status.WRONG, 'Demo apps did not open!'

        layout = {}
        layout['gtk_color_switcher'] = (0, 0, 250, 500)
        layout['gtk_special'] = (250, 0, 250, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(400, 400) # hover gtk_special
        self.socket.click_button('BTN_RIGHT', 'full') # make gtk_special always-on-top

        layout['gtk_color_switcher'] = (0, 0, 500, 500)
        layout['gtk_special'] = (200, 200, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(50, 50) # hover gtk_color_switcher
        self.socket.click_button('BTN_LEFT', 'full') # bring gtk_color_switcher to front => should fail

        if err := self.take_screenshot('1-setup'):
            return wt.Status.CRASHED, "Failed to take screenshot " + err

        if self._get_views() != ['gtk_color_switcher', 'gtk_special']:
            return wt.Status.WRONG, 'Demo apps crashed?'

        self.socket.press_key('KEY_1')
        if err := self.take_screenshot('2-empty-wset'):
            return wt.Status.CRASHED, "Failed to take screenshot " + err

        self.socket.press_key('KEY_2')
        if err := self.take_screenshot('3-back-to-wset2'):
            return wt.Status.CRASHED, "Failed to take screenshot " + err

        return wt.Status.OK, None
