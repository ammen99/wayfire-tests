#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        tiled = {'x': 10, 'y': 10, 'width': 1260, 'height': 700}
        full = {'x': 0, 'y': 0, 'width': 1280, 'height': 720}

        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients() # Wait for weston-terminals to open

        self.socket.press_key('KEY_T') # Tile
        self.wait_for_clients(2)
        g = self.socket.get_view_info('nil')['geometry']
        if g != tiled:
            return wt.Status.WRONG, 'Tiled weston-terminal does not have the correct size!' + str(g)

        self.socket.press_key('KEY_F') # Fullscreen
        self.wait_for_clients(2)
        g = self.socket.get_view_info('nil')['geometry']
        if g != full:
            return wt.Status.WRONG, 'Fullscreeen weston-terminal does not have the correct size!' + str(g)

        self.socket.press_key('KEY_F') # Unfullscreen
        self.wait_for_clients(2)
        g = self.socket.get_view_info('nil')['geometry']
        if g != tiled:
            return wt.Status.WRONG, 'Unfullscreened weston-terminal does not have the correct size!' + str(g)

        return wt.Status.OK, None
