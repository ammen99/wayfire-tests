#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This test opens weston-terminal and then maximizes and restores it in two different ways.
# It also checks that the window is restored correctly.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients(5)

        layout = {}
        layout['nil'] = (100, 200, 300, 300)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        initial_g = self.socket.get_view_info('nil')["geometry"]
        self.socket.press_key('KEY_C')
        self.wait_for_clients(2)

        maximized_g = self.socket.get_view_info('nil')["geometry"]
        if not wi.check_geometry(0, 100, 500, 400, maximized_g):
            return wt.Status.WRONG, "Invalid maximized geometry: " + str(maximized_g)

        self.socket.press_key('KEY_R')
        self.wait_for_clients(2)

        restored_g = self.socket.get_view_info('nil')["geometry"]
        if restored_g != initial_g:
            return wt.Status.WRONG, "Invalid restored geometry: " + str(restored_g)

        # Do the same, but this time fullscreen from the client
        layout = {}
        layout['nil'] = (200, 300, 250, 250)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        initial_g = self.socket.get_view_info('nil')["geometry"]

        self.socket.press_key('KEY_F11')
        self.wait_for_clients(2)
        fullscreen_g = self.socket.get_view_info('nil')["geometry"]
        if not wi.check_geometry(0, 0, 500, 500, fullscreen_g):
            return wt.Status.WRONG, "Invalid fullscreen geometry: " + str(fullscreen_g)

        self.socket.press_key('KEY_F11')
        self.wait_for_clients(2)

        restored_g = self.socket.get_view_info('nil')["geometry"]
        if restored_g != initial_g:
            return wt.Status.WRONG, "Invalid restored geometry after fullscreen: " + str(restored_g)

        return wt.Status.OK, None
