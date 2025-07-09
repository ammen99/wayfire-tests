#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens a terminal and a layer-shell view in the top layer.
# It then proceeds to fullscreen the terminal and ensure that it is above the
# layer-shell view (and receives input from it).
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk-layer-demo'):
            return wt.Status.SKIPPED, "Missing gtk-layer-demo"
        if not shutil.which('x11_click_to_close'):
            return wt.Status.SKIPPED, "Did you compile test clients?"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('gtk-layer-demo -l top -a lrt')
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=2)
        self.socket.press_key('KEY_F11') # Make weston-terminal fullscreen, so on top of gtk demo
        self.socket.run('x11_click_to_close x11 fullscreen')
        self.wait_for_clients_to_open(nr_clients=3)

        # gtk-layer-demo takes the top part of the screen.
        # However, the fullscreen x11 demo should cover that part,
        # so, if we click on 1,1, the x11 demo should close.
        self.socket.move_cursor(1, 1)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients(2)

        if self._get_views() != ['demo', 'org.freedesktop.weston.wayland-terminal']:
            return wt.Status.WRONG, \
                'x11_click_to_close did not get the click: ' + str(self._get_views())

        return wt.Status.OK, None
