#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return False

# Wayfire 1874
# Destroy surface while it has a delayed transaction
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        pid = self.socket.run('gtk_color_switcher gcs')['pid']
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.delay_next_tx()

        layout = {}
        layout['gcs'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients()
        os.kill(pid, signal.SIGKILL)

        # Wait for transaction to finish
        self.wait_ms(400)

        #self.socket.run('xterm')
        #self.wait_for_clients_to_open(nr_clients=1)
        return wt.Status.OK, None
