#!/bin/env python3

import wftest as wt
import wfutil as wu
import signal

def is_gui() -> bool:
    return False

# This test opens gedit and a gtk keyboard logger client side by side.
# Then, it opens a menu in gedit (xdg-popup) which should be automatically closed when clicking on the gtk logger client.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'weston-terminal'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _click_on(self, view_info):
        self.socket.move_cursor(view_info['geometry']['x'] + 5, view_info['geometry']['y'] + 5)
        self.socket.click_button('BTN_LEFT', 'full')

    def _run(self):
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1')
        editor = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'text-input')
        self.wait_for_clients_to_open(nr_clients=2)

        # Focus should be xterm
        layout = {}
        layout['gtk2'] = (0, 0, 500, 500)
        layout['gtk1'] = (500, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(125, 250)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()

        if self._get_views() != ['', 'gtk_logger', 'gtk_logger']:
            return wt.Status.WRONG, 'Popup menu did not open! ' + str(self._get_views())

        self.send_signal(editor.pid, signal.SIGKILL)
        self.wait_for_clients(2)
        self.socket.run('weston-terminal')
        self.wait_ms(600) # wait for unmap animation to end, the unmap animation is important, weston-terminal should run while it is active

        if self._get_views() != ['gtk_logger', 'nil']:
            return wt.Status.WRONG, 'Wrong views are open: ' + str(self._get_views())

        return wt.Status.OK, None
