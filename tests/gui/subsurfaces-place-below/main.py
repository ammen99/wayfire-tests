#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-subsurfaces'])

    def _run(self):
        self.socket.run('wleird-subsurfaces')
        self.wait_for_clients(2) # Wait for subsurfaces to start
        self.socket.move_cursor(111, 111) # Onto the red subsurface
        self.socket.click_button('BTN_LEFT', 'full') # Select red subsurface
        self.socket.move_cursor(101, 101) # Onto main surface
        self.socket.click_button('BTN_RIGHT', 'full') # Place red below main
        self.wait_for_clients(2) # Wait for subsurfaces to reoder
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
