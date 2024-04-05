#!/bin/env python3

import signal
import wftest as wt

def is_gui() -> bool:
    return False

# Delay view's map transaction, then kill it immediately
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.delay_next_tx()
        pid = self.socket.run('weston-terminal')['pid']
        self.wait_for_clients(6)
        self.send_signal(pid, signal.SIGKILL)
        self.wait_ms(1500) # wait for tx timeout
        return wt.Status.OK, None
