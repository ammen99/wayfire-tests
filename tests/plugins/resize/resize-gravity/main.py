#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens weston-terminal and resizes it from the top-left corner.
# It is expected that the window gravity is set to bottom-right.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_for_clients(2)

        layout = {}
        layout['org.freedesktop.weston.wayland-terminal'] = (100, 200, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(100, 200)
        self.socket.click_button('BTN_RIGHT', 'press')
        self.socket.move_cursor(200, 350) # Snap to right half
        self.wait_for_clients(3)
        if error := self.take_screenshot('resized'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
