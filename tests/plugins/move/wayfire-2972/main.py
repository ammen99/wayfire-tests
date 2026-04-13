#!/bin/env python3

import wftest as wt
import wfutil as wu
from wfipclib import check_geometry

def is_gui() -> bool:
    return False

# Wayfire #2972: wayfire crashes when attempting to maximize a dialog
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'dialog-shortcut')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_O')
        self.wait_for_clients_to_open(nr_clients=2)
        views = self.socket.list_views()
        v = [v for v in views if v['parent'] != -1][0]

        mx = v['geometry']['x'] + v['geometry']['width'] // 2
        my = v['geometry']['y'] + v['geometry']['height'] // 2
        self.click_and_drag('BTN_RIGHT', mx, my, 250, 0)
        self.wait_for_clients(2)

        # wayfire crashes
        info = self.socket.get_view_info_id(v['id'])
        if not check_geometry(0, 0, 500, 500, info['geometry']):
            return wt.Status.WRONG, 'Unexpected geometry: {}'.format(info['geometry'])

        return wt.Status.OK, None
