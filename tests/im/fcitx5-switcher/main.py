#!/bin/env python3

from wfipclib import WayfireIPCClient, get_msg_template
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gedit', 'fcitx5'])

    def _check_status_changed(self, ev_socket, status: bool, tryy: int):
        msg = ev_socket.read_message(self._ipc_duration * 2)
        if not msg or msg['state'] != status:
            return f'{tryy}: Switcher activation state is wrong: {str(msg)}'
        msg = ev_socket.read_message(self._ipc_duration)
        if msg:
            return f'{tryy}: Extra activation events: {str(msg)}'

        return None

    def _run(self):
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('dbus-launch --exit-with-session ./script.sh')
        self.wait_for_clients_to_open(nr_clients=2)

        ev_socket = WayfireIPCClient(self._socket_name)
        sub_cmd = get_msg_template('window-rules/events/watch')
        sub_cmd['data']['events'] = ['plugin-activation-state-changed']
        ev_socket.send_json(sub_cmd)

        # Press next twice => focus should remain on Gedit
        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_TAB', False)
        if msg := self._check_status_changed(ev_socket, True, 1):
            return wt.Status.WRONG, msg

        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTALT', False)
        if msg := self._check_status_changed(ev_socket, False, 2):
            return wt.Status.WRONG, msg

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'gedit':
            return wt.Status.WRONG, f'Gedit lost focus: {focused}'

        # This should switch focus
        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.set_key_state('KEY_TAB', True)
        if msg := self._check_status_changed(ev_socket, True, 3):
            return wt.Status.WRONG, msg

        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTALT', False)
        if msg := self._check_status_changed(ev_socket, False, 4):
            return wt.Status.WRONG, msg

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'nil':
            return wt.Status.WRONG, f'weston-terminal is not focused {focused}'

        return wt.Status.OK, None
