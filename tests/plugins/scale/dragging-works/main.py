#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens weston-terminal, starts scale and checks that we can drag the view
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        self.socket.press_key('KEY_T')
        self.wait_for_clients()

        # weston-terminal should be at the center
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(450, 450)
        self.wait_for_clients()

        if error := self.take_screenshot('1-scale-in-drag'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()

        if error := self.take_screenshot('2-scale-drag-released'):
            return wt.Status.CRASHED, error

        # Close scale
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients()

        if error := self.take_screenshot('3-scale-ended'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
