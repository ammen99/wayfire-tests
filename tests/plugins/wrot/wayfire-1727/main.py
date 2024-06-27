#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Wayfire #1727, #1693
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2)

        layout = {}
        layout['nil'] = (0, 0, 400, 500, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(150, 150)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(0, 50)
        self.socket.click_button('BTN_LEFT', 'release')

        if err := self.take_screenshot('1-wrot-rotated'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.socket.move_cursor(400, 400)

        if err := self.take_screenshot('2-wrot-ungrabbed-nothing-changes'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.socket.press_key('KEY_E')
        self.wait_for_clients()

        if err := self.take_screenshot('3-in-expo'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.socket.press_key('KEY_E')
        self.wait_for_clients()
        self.socket.press_key('KEY_R')

        if err := self.take_screenshot('4-reset'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        return wt.Status.OK, None
