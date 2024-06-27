#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        pid = self.socket.run('weston-terminal --shell=/bin/sh')['pid']
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_2')
        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)

        if self.socket.list_views():
            return wt.Status.WRONG, 'Not all views were closed?'

        return wt.Status.OK, None
