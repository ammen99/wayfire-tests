#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens xterm with decoration and resizes it from the top-left corner.
# It is expected that the window gravity is set to bottom-right.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['xterm'])

    def _run(self):
        self.socket.run('xterm')
        self.wait_for_clients(2)

        layout = {}
        layout['XTerm'] = (100, 200, 500, 500)
        print(self.socket.layout_views(layout))
        self.wait_for_clients(4)

        if error := self.take_screenshot('setup'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None

        self.socket.move_cursor(100, 200)
        self.socket.click_button('BTN_RIGHT', 'press')
        self.socket.move_cursor(200, 350)
        self.wait_for_clients(3)
        if error := self.take_screenshot('resized'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
