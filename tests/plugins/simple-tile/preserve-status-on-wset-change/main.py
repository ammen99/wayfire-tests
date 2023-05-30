#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Checks that after sending view to the second wset, it is tiled correctly.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        # Tile A and B on wset 1, A should be on the left
        self.socket.run('gtk_color_switcher a')
        self.wait_for_clients(2)
        self.socket.run('gtk_color_switcher b')
        self.wait_for_clients(2)

        # Tile C on wset 2
        self.socket.press_key('KEY_2')
        self.socket.run('gtk_color_switcher c')
        self.wait_for_clients(2)

        # Move B to wset 2
        self.socket.press_key('KEY_1')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_B')

        # Go to wset2 so that clients have time to update and receive frame callbacks
        self.socket.press_key('KEY_2')
        self.wait_for_clients(2)

        full_g = { 'x': 0, 'y': 0, 'width': 500, 'height': 500 }
        left_half_g = { 'x': 0, 'y': 0, 'width': 250, 'height': 500 }
        right_half_g = { 'x': 250, 'y': 0, 'width': 250, 'height': 500 }

        a = self.socket.get_view_info_title('a')['geometry']
        b = self.socket.get_view_info_title('b')['geometry']
        c = self.socket.get_view_info_title('c')['geometry']

        if  a != full_g:
            return wt.Status.WRONG, 'Wrong geometry for A on wset 1:' + str(a)
        if  b != right_half_g:
            return wt.Status.WRONG, 'Wrong geometry for B on wset 1:' + str(b)
        if  c != left_half_g:
            return wt.Status.WRONG, 'Wrong geometry for C on wset 1:' + str(c)

        return wt.Status.OK, None
