#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gedit', 'wl-paste'])

    def _run(self):
        self.socket.run('gedit')
        self.wait_for_clients_to_open(nr_clients=1)

        # type "abc" in gedit
        self.socket.press_key('KEY_A')
        self.socket.press_key('KEY_B')
        self.socket.press_key('KEY_C')
        self.wait_for_clients()

        # select all
        self.socket.press_key('C-KEY_A')

        # right click in the middle to open context menu (xdg-popup)
        info = self.socket.get_view_info('gedit')
        self.socket.move_cursor(info['geometry']['x'] + info['geometry']['width'] / 2,
                                info['geometry']['y'] + info['geometry']['height'] / 2)
        self.socket.click_button('BTN_RIGHT', 'full')
        if not self.wait_for_clients_to_open(nr_clients=2):
            return wt.Status.WRONG, 'Failed to open context menu'

        # Select all uppercase from menu: last item => first item in submenu
        self.socket.press_key('KEY_UP')
        self.socket.press_key('KEY_RIGHT')
        if not self.wait_for_clients_to_open(nr_clients=3):
            return wt.Status.WRONG, 'Failed to select uppercase'

        self.socket.press_key('KEY_ENTER')
        self.wait_ms(100)
        if len(self.socket.list_views()) != 1:
            return wt.Status.WRONG, 'Popups did not close?'

        # Select all, copy
        state = wu.copy_paste_gedit_state(self)
        if state != 'ABC\n':
            return wt.Status.WRONG, f'Wrong input in Gedit: ${state}$'

        return wt.Status.OK, None
