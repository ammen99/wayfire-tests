#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire issue #1700
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        # Toggle scale once
        self.socket.press_key('KEY_S')
        self.wait_for_clients()

        # Middle of the output and click middle button to close
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_MIDDLE', 'full')
        self.wait_for_clients(2)

        if views := self.socket.list_views():
            return wt.Status.WRONG, 'Views are still open? ' + str(views)

        return wt.Status.OK, None
