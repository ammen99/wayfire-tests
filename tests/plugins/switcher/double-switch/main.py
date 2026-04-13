#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        id1, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        _, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        id3, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        if self.socket.ipc_rules_get_focused()['id'] != id3:
            return wt.Status.WRONG, 'Focused window should be the last one created!'

        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.press_key('KEY_J')
        self.socket.press_key('KEY_J')
        self.socket.set_key_state('KEY_LEFTALT', False)
        self.wait_for_clients()
        if self.socket.ipc_rules_get_focused()['id'] != id1:
            return wt.Status.WRONG, 'Focused window should be the first one created!'

        return wt.Status.OK, None
