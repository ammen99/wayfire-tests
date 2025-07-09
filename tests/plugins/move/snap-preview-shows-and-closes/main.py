#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2) # Wait for terminals to start and be tiled

        layout = {}
        layout['org.freedesktop.weston.wayland-terminal'] = (0, 0, 200, 200)
        self.socket.layout_views(layout)
        self.wait_for_clients(1)

        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(1000, 250) # Snap to right half
        self.wait_ms(250) # wait for animation to stop
        if error := self.take_screenshot('preview-shown'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_ms(250) # wait for animation to stop
        if error := self.take_screenshot('snapped'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
