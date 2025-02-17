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
        id, _ = self.run_get_id('python3 ../resize-ratio/qtdemo.py 0 0 0 0')

        layout = {}
        layout[id] = (100, 100, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Make bigger with ratio
        self.click_and_drag('BTN_MIDDLE', 175, 175, 275, 375)
        self.wait_for_clients()
        g = self.socket.get_view_info_id(id)['geometry']
        if not wi.check_geometry(100, 100, 300, 300, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (100, 100, 300, 300): {}'.format(g)

        self.click_and_drag('BTN_MIDDLE', 275, 375, 175, 390)
        self.wait_for_clients()
        g = self.socket.get_view_info_id(id)['geometry']
        if not wi.check_geometry(100, 100, 200, 200, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (100, 100, 200, 200): {}'.format(g)

        # Hit minimum size (1x1)
        self.click_and_drag('BTN_RIGHT', 101, 101, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_id(id)['geometry']
        if not wi.check_geometry(299, 299, 1, 1, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (299, 299, 1, 1): {}'.format(g)

        return wt.Status.OK, None
