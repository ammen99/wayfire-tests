#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['kitty', 'gedit', 'fcitx5'])

    def _check_status_changed(self, ev_socket, status: bool, tryy: int):
        msg = ev_socket.read_message(self._ipc_duration * 2)
        if not msg or msg['state'] != status:
            return f'{tryy}: Fast-Switcher activation state is wrong: {str(msg)}'
        msg = ev_socket.read_message(self._ipc_duration)
        if msg:
            return f'{tryy}: Extra activation events: {str(msg)}'

        return None

    def _run(self):
        self.socket.run('kitty')
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('gedit')
        self.wait_for_clients_to_open(nr_clients=2)
        ev_socket = self.watch(['plugin-activation-state-changed'])

        # Press next twice => focus should remain on Gedit
        self.socket.set_key_state('KEY_LEFTALT', True)
        self.wait_for_clients(2)
        self.socket.press_key('KEY_ESC')
        self.wait_for_clients(2)
        if msg := self._check_status_changed(ev_socket, True, 1):
            return wt.Status.WRONG, msg

        self.socket.set_key_state('KEY_LEFTALT', False)
        if msg := self._check_status_changed(ev_socket, False, 2):
            return wt.Status.WRONG, msg

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'kitty':
            return wt.Status.WRONG, f'Weston-terminal not focused: {focused}'

        self.wait_for_clients(2)
        self.socket.press_key('KEY_J') # Can cause a crash if state is not correctly updated
        self.wait_for_clients(2)
        return wt.Status.OK, None
