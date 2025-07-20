#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Wayfire #1702
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2) # Wait for terminals to start and be tiled

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (0, 0, 200, 200)
        self.socket.layout_views(layout)
        self.wait_for_clients(1)

        self.socket.press_key('KEY_E') # Start expo
        self.wait_for_clients()

        self.socket.move_cursor(150, 150) # Actually, this is 50,50, but the output starts at 100,100
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(100, 100)

        if error := self.take_screenshot('drag-correct-position'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
