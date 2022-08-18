#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-subsurfaces'])

    def _run(self):
        self.socket.run('wleird-subsurfaces')
        self.wait_for_clients(2) # Wait for cursor to start
        self.socket.move_cursor(111, 111) # Onto the red subsurface
        self.socket.click_button('BTN_LEFT', 'full') # Select red subsurface
        self.socket.move_cursor(151, 151) # Onto blue surface
        self.socket.click_button('BTN_LEFT', 'full') # Place red above blue

        self.socket.move_cursor(101, 101) # Onto main surface
        self.socket.click_button('BTN_MIDDLE', 'press')
        self.socket.move_cursor(201, 101) # rotate with wrot
        self.socket.click_button('BTN_MIDDLE', 'release')

        self.wait_for_clients() # Wait for everything to settle down
        return wt.Status.OK, None
