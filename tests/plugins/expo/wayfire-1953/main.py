#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens one view, makes it always-on-top and ensures that Expo can handle that properly.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(4)

        self.socket.press_key('KEY_T')
        self.socket.press_key('KEY_E')
        self.wait_for_clients(1)
        self.socket.move_cursor(100, 100)

        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(150, 150)
        self.wait_for_clients()
        if error := self.take_screenshot('1-in-drag'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        if error := self.take_screenshot('2-expo-idle'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_E')
        self.wait_for_clients(1)
        self.socket.run('weston-terminal --shell=/bin/sh -m')
        self.wait_for_clients_to_open(nr_clients=2)

        if error := self.take_screenshot('3-still-on-top'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
