#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        id, _ = self.run_get_id('weston-terminal --shell=/bin/sh')

        layout = {}
        layout[id] = (-100, -100, 500, 500)
        self.socket.layout_views(layout)

        self.socket.press_key('KEY_M')
        self.wait_for_clients()

        self.socket.create_wayland_output()
        self.socket.destroy_wayland_output('WL-1')
        self.socket.press_key('KEY_S')
        self.wait_for_clients(4)
        self.socket.press_key('KEY_S')

        return wt.Status.OK, None
