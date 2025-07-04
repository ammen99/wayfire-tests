#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1702
class WTest(wt.WayfireTest):
    def prepare(self):
        return wt.Status.OK, None

    def _run(self):
        self.socket.sock.toggle_expo()
        self.wait_for_clients()
        self.socket.sock.toggle_expo()
        self.wait_for_clients()

        self.socket.sock.set_option_values({'core/vwidth': '3', 'core/vheight': '3'})
        self.socket.sock.toggle_expo()
        self.wait_for_clients()
        self.socket.sock.set_option_values({'core/vwidth': '2', 'core/vheight': '4'})
        self.wait_for_clients()
        self.socket.sock.toggle_expo()
        self.wait_for_clients()
        return wt.Status.OK, None
