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
        self.wait_ms(1500) # wait for tx timeout

        if msg := ev_socket.read_message(0.1):
            return wt.Status.WRONG, 'Extra message: ' + str(msg)

        return wt.Status.OK, None
