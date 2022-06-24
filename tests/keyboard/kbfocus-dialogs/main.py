#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test opens the gtk special client and uses it to open dialogs and then close them with
# simple keypresses. It also clicks a few times to attempt changing the focus, which should fail,
# as dialogs are always focused and not the main view.
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
        self.socket.run('WAYLAND_DEBUG=1 gtk_special a b &> /tmp/out')
        self.wait_for_clients(2)

        if self._get_views() != ['a', 'b']:
            return wt.Status.WRONG, 'Incorrect setup: ' + str(self._get_views())

        # Click on main window
        main_view = self.socket.get_view_info_title('a')
        # Focus main view should fail as it has open dialogs
        self._click_on(main_view)

        # Close dialog b
        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != ['a']:
            return wt.Status.WRONG, 'Dialog b was not closed: ' + str(self._get_views())
        self.wait_for_clients(10)

        # Open one dialog
        self.socket.press_key('KEY_O')
        self.wait_for_clients(10)
        if self._get_views() != ['a', 'auto0']:
            return wt.Status.WRONG, 'Main view did not get "o": ' + str(self._get_views())

        # Open nested dialog
        self.socket.press_key('KEY_O')
        self.wait_for_clients(3)
        if self._get_views() != ['a', 'auto0', 'auto1']:
            return wt.Status.WRONG, 'Dialog did not get "o": ' + str(self._get_views())

        # Should be no-op
        self._click_on(main_view)

        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != ['a', 'auto0']:
            return wt.Status.WRONG, 'Dialog auto1 id not get "q": ' + str(self._get_views())

        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != ['a']:
            return wt.Status.WRONG, 'Dialog auto0 did not get "q": ' + str(self._get_views())

        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != []:
            return wt.Status.WRONG, 'Main did not get "q": ' + str(self._get_views())

        return wt.Status.OK, None
