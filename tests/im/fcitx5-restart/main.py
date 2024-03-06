#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gedit', 'fcitx5', 'wl-paste'])

    def _run(self):
        pid = self.socket.run('dbus-launch --exit-with-session ../fcitx-wrapper/start-fcitx5.sh')['pid']
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

        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)
        self.socket.run('dbus-launch --exit-with-session ../fcitx-wrapper/start-fcitx5.sh')['pid']
        self.wait_for_clients(4)

        self.socket.press_key('KEY_A')
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients(2)

        # Select all, copy
        self.socket.press_key('C-KEY_A')
        self.wait_for_clients()
        self.socket.press_key('C-KEY_C')
        self.wait_for_clients()

        self.socket.run('wl-paste > gedit-state.txt')
        self.wait_for_clients(4)

        with open('gedit-state.txt') as f:
            state = f.read()
            if state != '\\u98ce\\u683c\\u554a\n':
                return wt.Status.WRONG, f'Wrong input in Gedit: ${state}$'

        return wt.Status.OK, None
