#!/bin/env python3

from wfipclib import check_geometry
import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1303
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients(2)

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (200, 200, 300, 300)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        initial_g = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['geometry']

        self.click_and_drag('BTN_RIGHT', 250, 207, 250, 0) # Drag and snap to top => maximize
        self.wait_for_clients(2)

        maximized = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['geometry']
        if not check_geometry(0, 0, 500, 500, maximized):
            return wt.Status.WRONG, 'weston-terminal has wrong maximized geometry: ' + str(maximized)

        # Unmaximize => should be in the center again
        self.socket.press_key('KEY_M')
        self.wait_for_clients(2)
        restored = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['geometry']
        if initial_g != restored:
            return wt.Status.WRONG, 'weston-terminal has wrong restored geometry: ' + str(restored)

        return wt.Status.OK, None
