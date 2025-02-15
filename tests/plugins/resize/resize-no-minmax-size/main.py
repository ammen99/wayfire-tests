#!/bin/env python3

import wfipclib as wi
import wftest as wt

def is_gui() -> bool:
    return False

# Make sure that resize does not crash without min/max size set
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        id, _ = self.run_get_id('weston-terminal --shell=/bin/sh')

        layout = {}
        layout[id] = (100, 100, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Make bigger
        self.click_and_drag('BTN_RIGHT', 175, 175, 275, 275)
        self.wait_for_clients()

        # Hit minimum size (0x0)
        self.click_and_drag('BTN_RIGHT', 101, 101, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_id(id)['geometry']
        if not wi.check_geometry(100, 196, 202, 123, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (675, 350, 25, 50): {}'.format(g)

        return wt.Status.OK, None
