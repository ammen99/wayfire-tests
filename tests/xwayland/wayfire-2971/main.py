#!/bin/env python3

import wftest as wt
from wfipclib import check_geometry

def is_gui() -> bool:
    return False

# Xwayland view configures its start position when not on 0,0 workspace
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_click_to_close'])

    def _run(self):
        self.socket.sock.set_workspace(2, 1)
        # 100ms delay after map before configure
        id, _ = self.run_get_id('x11_click_to_close x11 100 200 200 200 100000')
        self.wait_ms(200)

        g = self.socket.get_view_info_id(id)
        if not check_geometry(100, 200, 200, 200, g['geometry']):
            return wt.Status.WRONG, "Unexpected geometry: {}".format(g['geometry'])

        return wt.Status.OK, None
