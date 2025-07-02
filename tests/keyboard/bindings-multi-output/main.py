#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test starts two clients on two different outputs.
# It then proceeds to check that the active output (one last clicked on) receives
# the predefined keybindings for closing a view, and the other output does not.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_special'):
            return wt.Status.SKIPPED, "Missing gtk_special (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        self.socket.run('gtk_special a')
        self.socket.run('gtk_special b')
        self.wait_for_clients_to_open(nr_clients=2)
        if self._get_views() != ['a', 'b']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # Create WL-2
        self.socket.create_wayland_output()

        # position the views (a -> WL-1, b-> WL-2)
        layout = {}
        layout['a'] = (0, 0, 100, 100, 'WL-1')
        layout['b'] = (0, 0, 100, 100, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Go to WL-1
        self.socket.move_cursor(500, 0)
        self.socket.click_button('BTN_LEFT', 'full')
        # Press super+KEY_H, we have configured this to core/close_top_view
        self.socket.press_key('W-KEY_H')
        self.wait_for_clients(2)
        if self._get_views() != ['b']:
            return wt.Status.WRONG, 'Wrong app got the key combo! ' + str(self._get_views())

        # Pressing again, but the output WL-1 is still focused and does not contain 'b'
        self.socket.press_key('W-KEY_H')
        self.wait_for_clients(2)
        if self._get_views() != ['b']:
            return wt.Status.WRONG, 'Did focus switch to the other output? ' + str(self._get_views())

        self._click_on(self.socket.get_view_info_title('b'))
        self.socket.press_key('W-KEY_H')
        self.wait_for_clients(2)
        if self._get_views() != []:
            return wt.Status.WRONG, 'After output switch, cannot close second app! ' + str(self._get_views())

        return wt.Status.OK, None
