#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens two instances of weston-terminal and tries to fullscreen one of them.
# They are both added to simple-tile, and fullscreening happens via simple-tile.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('weston-terminal')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients() # Wait for weston-terminals to open
        self.socket.press_key('KEY_F') # Fullscreen any of the two
        self.wait_for_clients(2)
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
