#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_F') # Fullscreen
        self.wait_for_clients(2)
        g = self.socket.get_view_info('org.freedesktop.weston.wayland-terminal')['geometry']
        if not wi.check_geometry(0, 0, 1280, 720, g):
            return wt.Status.WRONG, 'Fullscreeen weston-terminal does not have the correct size!' + str(g)

        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_for_clients() # wait for resize after initial map

        g = self.socket.get_view_info('org.freedesktop.weston.wayland-terminal')['geometry']
        if not wi.check_geometry(50, 50, 585, 620, g):
            return wt.Status.WRONG, 'Unfullscreened weston-terminal does not have the correct size!' + str(g)

        g = self.socket.get_view_info('gtk_color_switcher')['geometry']
        if not wi.check_geometry(645, 50, 585, 620, g):
            return wt.Status.WRONG, 'Unfullscreened gcs does not have the correct size!' + str(g)

        return wt.Status.OK, None
