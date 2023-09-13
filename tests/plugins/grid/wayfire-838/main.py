#!/bin/env python3

import wfipclib as wi
import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #838
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=1)

        # Tile left
        self.socket.press_key('KEY_L')

        self.wait_for_clients(2)
        g = self.socket.get_view_info('gtk_color_switcher')['geometry']
        if not wi.check_geometry(0, 0, 500, 500, g):
            return wt.Status.WRONG, 'Not tiled: ' + str(g)

        # Resize to 250x250
        self.socket.move_cursor(0, 0)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'release')

        self.wait_for_clients(2)
        g = self.socket.get_view_info('gtk_color_switcher')['geometry']
        if not wi.check_geometry(250, 250, 250, 250, g):
            return wt.Status.WRONG, 'Not resized: ' + str(g)

        # Open an exclusive zone client, triggering a change in workarea
        # This should't resize gcs, since it is no longer tiled
        self.socket.run('wleird-layer-shell -a top -x 100 -h 100')
        self.wait_for_clients_to_open(nr_clients=2)

        self.wait_for_clients(2)
        g = self.socket.get_view_info('gtk_color_switcher')['geometry']
        if not wi.check_geometry(250, 250, 250, 250, g):
            return wt.Status.WRONG, 'Resized after tiling: ' + str(g)

        return wt.Status.OK, None
