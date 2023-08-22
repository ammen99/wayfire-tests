#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return False

# Wayfire 1856, Wayfire-plugins-extra #181
# The idea of this test is to open a client and start a transaction, then kill the client while the transaction is running.
# This triggers an unmap and a destroy signal, we have to guarantee unmap is first
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wleird-slow-ack-configure'])

    def _run(self):
        self.socket.run('weston-terminal -m')
        self.wait_for_clients(2)
        slowack = self.socket.run('wleird-slow-ack-configure 300 400')["pid"]
        self.wait_for_clients(2)

        layout = {}
        layout['wleird-slow-ack-configure'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        os.kill(slowack, signal.SIGKILL)

        # Wait for transaction to finish
        self.wait_ms(150)
        print(self.socket.list_views())

        # Click on weston-terminal
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        return wt.Status.OK, None
