#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wleird-gamma-blend'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('weston-terminal')
        self.wait_for_clients(2) # Wait for terminals to start and be tiled
        self.socket.run('wleird-gamma-blend') # Start on top
        self.wait_for_clients(2) # Wait for it to start

        layout = {}
        layout['wleird-gamma-blend'] = (300, 300, 400, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(1)

        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(1)
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
