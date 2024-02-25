#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gedit', 'fcitx5'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('dbus-launch --exit-with-session ./script.sh')
        self.wait_for_clients_to_open(nr_clients=2)

        # Press next twice => focus should remain on weston-terminal
        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_N', False)
        self.wait_for_clients(2)

        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTALT', False)
        self.wait_for_clients(2)

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'gedit':
            return wt.Status.WRONG, f'Gedit lost focus: {focused}'

        # This should switch focus
        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTALT', False)
        self.wait_for_clients(2)
        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'nil':
            return wt.Status.WRONG, f'weston-terminal is not focused {focused}'

        return wt.Status.OK, None
