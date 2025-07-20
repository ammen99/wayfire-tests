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
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2)

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (0, 0, 200, 200, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        for i in range(2):
            self.click_and_drag('BTN_RIGHT', 50, 50, 750, 60) # Add 200, 10 to the view geometry
            self.wait_for_clients()
            g = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['geometry']
            if g['x'] != 200 or g['y'] != 10:
                return wt.Status.WRONG, f'Try #{i}: weston-terminal has invalid geometry after dragging with binding: {str(g)}'

            # Drag via titlebar this time, back to the first output
            sx = 500 + g['x'] + 10
            sy = g['y'] + 10
            self.click_and_drag('BTN_LEFT', sx, sy, 10, 10)
            self.wait_for_clients()
            g = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['geometry']
            if g['x'] != 0 or g['y'] != 0:
                return wt.Status.WRONG, f'Try #{i}: weston-terminal has invalid geometry after dragging by titlebar: {str(g)}'

        return wt.Status.OK, None
