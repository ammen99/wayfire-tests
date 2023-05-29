#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_special', 'gtk_color_switcher'])

    def _run(self):
        self.socket.run('gtk_special a')
        self.wait_for_clients(2)

        self.socket.press_key('KEY_2')
        self.socket.run('gtk_color_switcher')
        self.wait_for_clients(2)

        # If give them opportunity to resize if simple-tile did a mistake
        self.socket.press_key('KEY_1')
        self.wait_for_clients(2)

        full_g = { 'x': 0, 'y': 0, 'width': 500, 'height': 500 }
        geometry_special = self.socket.get_view_info('gtk_special')['geometry']
        geometry_switcher = self.socket.get_view_info('gtk_color_switcher')['geometry']

        if  geometry_special != full_g:
            return wt.Status.WRONG, 'Wrong geometry for gtk_special on wset 1:' + str(geometry_special)

        if  geometry_switcher != full_g:
            return wt.Status.WRONG, 'Wrong geometry for gtk_color_switcher on wset 2:' + str(geometry_switcher)

        return wt.Status.OK, None
