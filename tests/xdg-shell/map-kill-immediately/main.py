#!/bin/env python3

import signal
import wftest as wt

def is_gui() -> bool:
    return False

# Delay view's map transaction, then kill it immediately
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def get_subtests(self):
        return [('xdg-shell', 'weston-terminal'),
                ('xwayland', 'xterm')]

    def _run(self):
        ev_socket = self.watch(['view-mapped', 'view-unmapped'])
        self.socket.delay_next_tx()
        pid = self.socket.run(self.subtest_data)['pid']
        self.wait_for_clients(6)

        mapped = self._get_mapped_views()
        if mapped:
            return wt.Status.WRONG, 'No views should be mapped at this point: ' + str(mapped)

        self.send_signal(pid, signal.SIGKILL)
        self.wait_ms(1100) # wait for tx timeout

        if msg := ev_socket.read_message(0.1):
            return wt.Status.WRONG, 'Extra message: ' + str(msg)

        pid = self.socket.run(self.subtest_data)['pid']
        self.wait_for_clients_to_open(nr_clients=1)
        msg = ev_socket.read_message(0.1)
        if not msg or msg['event'] != 'view-mapped' or msg['view']['mapped'] != True:
            return wt.Status.WRONG, 'View not mapped properly: ' + str(msg)

        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)
        msg = ev_socket.read_message(0.1)
        if not msg or msg['event'] != 'view-unmapped' or msg['view']['mapped'] != False:
            return wt.Status.WRONG, 'View not unmapped properly: ' + str(msg)

        return wt.Status.OK, None
