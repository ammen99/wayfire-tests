#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_logger', 'fcitx5', 'wl-paste'])

    def _check_status_changed(self, ev_socket, status: bool, tryy: int):
        msg = ev_socket.read_message(self._ipc_duration * 2)
        if not msg or msg['state'] != status:
            return f'{tryy}: Switcher activation state is wrong: {str(msg)}'
        msg = ev_socket.read_message(self._ipc_duration)
        if msg:
            return f'{tryy}: Extra activation events: {str(msg)}'

        return None

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('../fcitx-wrapper/start-fcitx5.sh')
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'text-input')
        self.wait_for_clients_to_open(nr_clients=2)

        self.wait_for_clients(4) # Wait for IM
        ev_socket = self.watch(['plugin-activation-state-changed'])

        # Send a key to IM, grab keyboard, type something
        self.socket.press_key('KEY_J')
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients(2)

        # Press next twice => focus should remain on Gedit
        self.socket.set_key_state('KEY_LEFTMETA', True)
        self.socket.set_key_state('KEY_TAB', True)

        # Random keys during grab should be ignored
        self.socket.press_key('KEY_J')
        self.wait_for_clients(2)

        self.socket.set_key_state('KEY_TAB', False)
        if msg := self._check_status_changed(ev_socket, True, 1):
            return wt.Status.WRONG, msg

        self.socket.set_key_state('KEY_TAB', True)
        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTMETA', False)
        if msg := self._check_status_changed(ev_socket, False, 2):
            return wt.Status.WRONG, msg

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'gtk_logger':
            return wt.Status.WRONG, f'gtk_logger lost focus: {focused}'

        # We should be able to type in Gedit now
        self.wait_for_clients(4) # wait for initial handshake with IM
        self.socket.press_key('KEY_J')
        self.socket.press_key('KEY_SPACE')
        self.wait_for_clients(2)

        # Select all, copy
        state = wu.copy_paste_gedit_state(self)
        if state != '\\u53ca\\u53ca\n':
            return wt.Status.WRONG, f'Wrong input in Gedit: ${state}$'

        # This should switch focus
        self.socket.set_key_state('KEY_LEFTMETA', True)
        self.socket.set_key_state('KEY_TAB', True)
        if msg := self._check_status_changed(ev_socket, True, 3):
            return wt.Status.WRONG, msg

        self.socket.set_key_state('KEY_TAB', False)
        self.socket.set_key_state('KEY_LEFTMETA', False)
        if msg := self._check_status_changed(ev_socket, False, 4):
            return wt.Status.WRONG, msg

        focused = self.socket.ipc_rules_get_focused()['info']
        if not focused or focused['app-id'] != 'org.freedesktop.weston.wayland-terminal':
            return wt.Status.WRONG, f'weston-terminal is not focused {focused}'

        return wt.Status.OK, None
