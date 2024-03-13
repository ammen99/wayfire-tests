#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# This test opens gedit and a gtk keyboard logger client side by side.
# Then, it opens a menu in gedit (xdg-popup) which should be automatically closed when clicking on the gtk logger client.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'gedit'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard pointer')
        self.socket.run('gedit')
        if not self.wait_for_clients_to_open(nr_clients=2):
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # Focus should be xterm
        layout = {}
        layout['gedit'] = (0, 0, 500, 500)
        layout['gtk_logger'] = (500, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(125, 250)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()

        if not self.wait_for_clients_to_open(nr_clients=3):
            return wt.Status.WRONG, 'Popup menu did not open! ' + str(self._get_views())

        gtk.reset_logs()
        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients()

        if self._get_views() != ['gedit', 'gtk_logger']:
            return wt.Status.WRONG, 'Popup menu did not close! ' + str(self._get_views())

        try:
            gtk.expect_unordered_lines_throw(['keyboard-enter', 'pointer-enter'])
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
