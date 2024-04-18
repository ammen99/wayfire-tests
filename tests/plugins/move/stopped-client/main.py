#!/bin/env python3

import signal
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        id, pid = self.run_get_id('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)

        self.watch(['plugin-activation-state-changed'])
        geom = self.socket.get_view_info_id(id)['geometry'] # type: ignore

        self.send_signal(pid, signal.SIGSTOP)
        self.wait_for_clients(2)
        self.click_and_drag('BTN_LEFT', geom['x'] + 10, geom['y'] + 10, 450, 450)
        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGCONT)

        assert self.ev_socket
        msg = self.ev_socket.read_message(self._ipc_duration * 2)
        if msg:
            return wt.Status.WRONG, f'Extra activation events: {str(msg)}'

        return wt.Status.OK, None
