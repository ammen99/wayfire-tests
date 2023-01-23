#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1695
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        layout = {}
        layout['nil'] = (0, 0, 200, 200, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(750, 50)
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)

        g = self.socket.get_view_info('nil')['geometry']
        if g['x'] != 200 or g['y'] != 0:
            return wt.Status.WRONG, 'weston-terminal has invalid geometry: ' + str(g)

        return wt.Status.OK, None
