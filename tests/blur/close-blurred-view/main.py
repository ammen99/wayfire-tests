#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['terminator', 'wf-background'])

    def _run(self):
        self.socket.run('terminator')
        self.socket.run('wf-background')
        self.wait_for_clients(2)

        self.socket.set_key_state('KEY_LEFTCTRL', True)
        self.socket.set_key_state('KEY_D', True)
        self.socket.set_key_state('KEY_D', False)
        self.socket.set_key_state('KEY_LEFTCTRL', False)
        self.wait_for_clients(20)

        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
