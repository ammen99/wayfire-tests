#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test opens a terminal and a layer-shell view in the top layer.
# It then proceeds to fullscreen the terminal and ensure that it is above the
# layer-shell view (and receives input from it).
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_special'):
            return wt.Status.SKIPPED, "Missing gtk_special (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('gtk_special a b')
        self.wait_for_clients(5)

        if self._get_views() != ['a', 'b']:
            return wt.Status.WRONG, 'Missing views: ' + str(self._get_views())

        main_view = self.socket.get_view_info_title('a')
        dialog = self.socket.get_view_info_title('b')

        # Click on main view => if compositor buggy, it will come to the front
        self.socket.move_cursor(main_view['geometry']['x'] + 5, main_view['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

        # Close dialog by clicking on it
        self.socket.move_cursor(dialog['geometry']['x'] + 5, dialog['geometry']['y'] + 5)
        self.socket.click_button('BTN_RIGHT', 'full')

        self.wait_for_clients(1)
        if self._get_views() != ['a']:
            return wt.Status.WRONG, \
                'Dialog did not get the click: ' + str(self._get_views())

        return wt.Status.OK, None
