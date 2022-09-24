#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-background'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('wf-background')
        self.wait_for_clients(4)

        layout = {}
        layout['nil'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(4)

        self.socket.press_key('KEY_E')
        self.wait_for_clients(1)
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(500, 250) # Move to the center
        self.wait_for_clients()
        if error := self.take_screenshot('in-drag'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        if error := self.take_screenshot('idle'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
