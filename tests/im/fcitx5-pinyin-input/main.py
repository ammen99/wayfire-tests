#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gedit', 'fcitx5', 'wl-paste'])

    def _run(self):
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')
        self.socket.run('gedit')
        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_for_clients(2) # wait for im

        # Default layout is pinyin => enter a few chinese symbols
        self.socket.press_key('KEY_F')
        self.wait_for_clients()
        self.socket.press_key('KEY_G')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()
        self.socket.press_key('KEY_F')
        self.wait_for_clients()
        self.socket.press_key('KEY_H')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()

        # Switch to english layout, type english letters, space
        self.socket.press_key('C-KEY_SPACE')
        self.wait_for_clients()

        self.socket.press_key('KEY_A')
        self.wait_for_clients()
        self.socket.press_key('KEY_B')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()

        # Switch back to pinyin, type a few more chinese symbols and space
        self.socket.press_key('C-KEY_SPACE')
        self.wait_for_clients()
        self.socket.press_key('KEY_A')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()

        # Select all, copy
        state = wu.copy_paste_gedit_state(self)
        if state != '\\u98ce\\u683c\\u8fd4\\u56deab \\u554a \n':
            return wt.Status.WRONG, f'Wrong input in Gedit: ${state}$'

        return wt.Status.OK, None
