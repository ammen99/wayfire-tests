#!/bin/env python3

import wftest as wt
import wfutil as wu
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gedit', 'fcitx5', 'wl-paste'])

    def _run(self):
        pid = self.socket.run('../fcitx-wrapper/start-fcitx5.sh')['pid']
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'text-input')
        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_for_clients(4) # for fcitx5

        # Default layout is pinyin => enter a few chinese symbols
        self.socket.press_key('KEY_F')
        self.wait_for_clients()
        self.socket.press_key('KEY_G')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients()

        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')['pid']
        self.wait_for_clients(4)

        self.socket.press_key('KEY_A')
        self.wait_for_clients()
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients(2)

        # Select all, copy
        state = wu.copy_paste_gedit_state(self)
        if state != '\\u98ce\\u683c\\u554a\n':
            return wt.Status.WRONG, f'Wrong input in Gedit: ${state}$'

        return wt.Status.OK, None
