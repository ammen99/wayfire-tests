#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client opens weston-terminal and a test client, then minimizes
# weston-terminal and checks that it is not visible.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wleird-layer-shell'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('wleird-layer-shell -l bottom -c green -a top -a left')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_for_clients(2) # Wait for tiled

        layout = {}
        layout['org.freedesktop.weston.wayland-terminal'] = (0, 0, 200, 200)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        geom = self.socket.get_view_info('org.freedesktop.weston.wayland-terminal')['geometry']
        self.socket.move_cursor(geom['width'] - 70, 10)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        if not self.socket.get_view_info('org.freedesktop.weston.wayland-terminal')['minimized']:
            return wt.Status.WRONG, 'weston-terminal was not minimized!'

        if err := self.take_screenshot('minimized-does-not-show'):
            return wt.Status.WRONG, err

        self.socket.set_key_state('KEY_LEFTALT', True)
        self.socket.press_key('KEY_TAB')
        self.wait_for_clients()
        if err := self.take_screenshot('switcher-shows-minimized'):
            return wt.Status.CRASHED, err

        self.socket.set_key_state('KEY_LEFTALT', False)
        self.wait_for_clients()
        if err := self.take_screenshot('restored'):
            return wt.Status.CRASHED, err

        return wt.Status.OK, None
