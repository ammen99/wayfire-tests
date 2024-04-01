#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Add a delayed tile transaction for a xwayland view, then close it while the transaction is running.
# The decoration plugin will try to update tiled status when the transaction times out, but the XW subobject will be gone already.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_click_to_close'])

    def _run(self):

        pid = self.socket.run('x11_click_to_close x11 0 0 200 200')['pid']
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.delay_next_tx()
        self.socket.press_key('KEY_M')
        self.send_signal(pid, signal.SIGKILL)
        self.wait_ms(300) # wait for tx timeout

        if self.socket.list_views():
            return wt.Status.WRONG, "Clients are still open?"

        return wt.Status.OK, None
