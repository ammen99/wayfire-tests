#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'text-input')
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=2)

        # Focus should be xterm
        layout = {}
        layout['gtk1'] = (0, 0, 500, 500)
        layout['gtk2'] = (500, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(125, 250)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients_to_open(nr_clients=3, message='popup menu should be open now')

        gtk.reset_logs()
        self.socket.press_key('S-KEY_TAB')
        self.wait_for_clients()

        if self._get_views() != ['gtk_logger', 'gtk_logger']:
            return wt.Status.WRONG, 'Popup menu did not close! ' + str(self._get_views())

        try:
            gtk.expect_line_throw('keyboard-enter')
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
