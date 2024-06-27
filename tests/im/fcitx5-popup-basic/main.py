#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gedit', 'fcitx5'])

    def _run(self):
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'text-input')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.press_key('KEY_R') # Make sure gedit is not maximized!
        self.wait_for_clients(4)

        # Press next twice => focus should remain on Gedit
        self.socket.set_key_state('KEY_LEFTCTRL', True)
        self.socket.set_key_state('KEY_SPACE', True)
        self.socket.set_key_state('KEY_SPACE', False)
        self.socket.set_key_state('KEY_LEFTCTRL', False)

        self.wait_for_clients_to_open(nr_clients=2, message='IM popup did not show!')
        if err := self.take_screenshot('1-shown'):
            return wt.Status.WRONG, err

        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients(2)
        if err := self.take_screenshot('2-hidden'):
            return wt.Status.WRONG, err

        return wt.Status.OK, None
