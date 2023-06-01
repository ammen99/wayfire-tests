#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1695
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def click_and_drag(self, button, start_x, start_y, end_x, end_y):
        dx = end_x - start_x
        dy = end_y - start_y

        self.socket.move_cursor(start_x, start_y)
        self.socket.click_button(button, 'press')
        for i in range(11):
            self.socket.move_cursor(start_x + dx * i // 10, start_y + dy * i // 10)
        self.socket.click_button(button, 'release')

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('weston-terminal')
        self.wait_for_clients(2)

        layout = {}
        layout['nil'] = (0, 0, 200, 200, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        for i in range(2):
            self.click_and_drag('BTN_RIGHT', 50, 50, 750, 60) # Add 200, 10 to the view geometry
            g = self.socket.get_view_info('nil')['geometry']
            if g['x'] != 200 or g['y'] != 10:
                return wt.Status.WRONG, f'Try #{i}: weston-terminal has invalid geometry after dragging with binding: {str(g)}'

            # Drag via titlebar this time, back to the first output
            sx = 500 + g['x'] + 10
            sy = g['y'] + 10
            self.click_and_drag('BTN_LEFT', sx, sy, 10, 10)
            g = self.socket.get_view_info('nil')['geometry']
            if g['x'] != 0 or g['y'] != 0:
                return wt.Status.WRONG, f'Try #{i}: weston-terminal has invalid geometry after dragging by titlebar: {str(g)}'

        return wt.Status.OK, None
