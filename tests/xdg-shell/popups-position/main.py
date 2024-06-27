#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test opens gedit and a gtk keyboard logger client side by side.
# Then, it opens a menu in gedit (xdg-popup) which should be automatically closed when clicking on the gtk logger client.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)

        terminal = self.socket.get_view_info('nil')

        sx, sy = terminal['bbox']['x'] + 200, terminal['bbox']['y'] + 200
        self.socket.move_cursor(sx, sy)
        self.socket.click_button('BTN_RIGHT', 'full')

        self.wait_for_clients_to_open(nr_clients=2)


        g = self.socket.get_view_info('')['geometry']

        dx, dy = g['x'] - sx, g['y'] - sy

        if dx != -48 or dy != -48:
            return wt.Status.WRONG, 'Popup menu is not positioned properly: dx={}, dy={}'.format(dx, dy)

        return wt.Status.OK, None
