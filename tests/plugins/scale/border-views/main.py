#!/bin/env python3

import signal
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.run_get_id('weston-terminal')
        id2, pid2 = self.run_get_id('weston-terminal')

        layout = {}
        layout[id2] = (450, 450, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.press_key('KEY_T')
        self.wait_for_clients()
        self.send_signal(pid2, signal.SIGKILL)
        self.wait_for_clients(2)

        self.socket.press_key('KEY_LEFT')
        return wt.Status.OK, None
