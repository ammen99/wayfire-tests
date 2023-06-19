#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens the gtk special client and uses it to open dialogs and then close them with
# simple keypresses. It also clicks a few times to attempt changing the focus, which should fail,
# as dialogs are always focused and not the main view.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_special'):
            return wt.Status.SKIPPED, "Missing gtk_special (Did you compile test clients?)"
        if not shutil.which('x11_click_to_close'):
            return wt.Status.SKIPPED, "Did you compile test clients?"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        self.socket.run('gtk_special a')
        self.socket.run('gtk_special b')
        self.socket.run('x11_click_to_close x11 500 500 200 200')
        self.wait_for_clients(2)
        if self._get_views() != ['a', 'b', 'x11']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # Focus should be xterm
        self._click_on(self.socket.get_view_info_title('x11'))
        self.wait_for_clients()
        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != ['a', 'b', 'x11']:
            return wt.Status.WRONG, 'Demo did not get keyboard input: ' + str(self._get_views())

        self._click_on(self.socket.get_view_info_title('b'))
        self.wait_for_clients()
        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != ['b', 'x11'] and self._get_views() != ['a', 'x11']:
            return wt.Status.WRONG, 'GTK demos did not get keyboard input: ' + str(self._get_views())

        return wt.Status.OK, None
