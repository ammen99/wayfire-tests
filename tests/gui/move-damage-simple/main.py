#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-subsurfaces'])

    def _run(self):
        self.socket.run('wleird-subsurfaces')
        self.wait_for_clients(2) # Wait for subsurfaces to start

        layout = {}
        layout['wleird-subsurfaces'] = (200, 200, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        return wt.Status.OK, None
