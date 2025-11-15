#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['swaylock'])

    def _run(self):
        pid = self.socket.run('WAYLAND_DEBUG=1 swaylock &> /tmp/log')['pid']
        self.wait_for_clients(2)
        # wayfire crashes?
        self.send_signal(pid, signal.SIGUSR1)
        self.wait_for_clients(2)

        self.socket.create_wayland_output()
        self.socket.run('swaylock')['pid']
        self.wait_for_clients(2)
        self.socket.destroy_wayland_output('WL-1')
        self.socket.destroy_wayland_output('WL-2')
        self.wait_for_clients(2)

        return wt.Status.OK, None
