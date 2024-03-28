#!/bin/env python3

from wfipclib import WayfireIPCClient, get_msg_template
import wftest as wt

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _check_status_changed(self, ev_socket, status: bool):
        msg = ev_socket.read_message(self._ipc_duration * 2)
        if not msg or msg['state'] != status:
            return f'Simple-tile activation state is wrong: {str(msg)}'
        return None

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=2)

        ev_socket = WayfireIPCClient(self._socket_name)
        sub_cmd = get_msg_template('window-rules/events/watch')
        sub_cmd['data']['events'] = ['plugin-activation-state-changed']
        ev_socket.send_json(sub_cmd)

        self.click_and_drag('BTN_LEFT', 125, 125, 450, 5, release=False)
        self.wait_ms(300) # hardcoded preview animation

        if self._check_status_changed(ev_socket, True):
            return wt.Status.WRONG, 'simple-tile not activated!'

        self.socket.move_cursor(125, 125)
        self.wait_ms(300) # hardcoded preview animation

        msg = ev_socket.read_message(self._ipc_duration * 2)
        if msg:
            return wt.Status.WRONG, f'Simple-tile extra activation events: {str(msg)}'

        return wt.Status.OK, None
