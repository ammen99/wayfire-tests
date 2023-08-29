#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return False

# Wayfire 1874
# Destroy xwayland surface while it has a delayed transaction
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['xterm'])

    def _run(self):
        self.socket.run('xterm')
        self.wait_for_clients_to_open(nr_clients=1)

        pid = self.socket.xwayland_pid()['pid'] + 1
        print(pid)
        self.socket.delay_next_tx()

        layout = {}
        layout['XTerm'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients()
        os.kill(pid, signal.SIGKILL)

        # Wait for transaction to finish
        self.wait_ms(1500)
        self.socket.ping()
        return wt.Status.OK, None
