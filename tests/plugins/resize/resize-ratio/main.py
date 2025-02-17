#!/bin/env python3

import wfipclib as wi
import wftest as wt

def is_gui() -> bool:
    return False

# This test tries to make sure that resizing works, with or without preserving ratio, while honoring min/max sizes.
class WTest(wt.WayfireTest):
    def prepare(self):
        import importlib
        spec = importlib.util.find_spec('PyQt5.QtWidgets') # type: ignore
        if spec:
            return wt.Status.OK, None
        else:
            return wt.Status.SKIPPED, 'PyQt5.QtWidgets missing'

    def _run(self):
        self.socket.run('python3 qtdemo.py 25 50 600 300')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['test'] = (100, 100, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Ensure we hit max size
        self.click_and_drag('BTN_RIGHT', 175, 175, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(100, 100, 600, 300, g):
            return wt.Status.WRONG, 'geometry mismatch after BR resize to (100, 100, 600, 300): {}'.format(g)

        # Hit minimum size
        self.click_and_drag('BTN_RIGHT', 101, 101, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(675, 350, 25, 50, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (675, 350, 25, 50): {}'.format(g)

        # Next try to preserve ratio
        layout = {}
        layout['test'] = (100, 100, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.click_and_drag('BTN_MIDDLE', 175, 175, 275, 200)
        self.wait_for_clients()
        g = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(100, 100, 200, 200, g):
            return wt.Status.WRONG, 'geometry mismatch after BR ratio resize to (100, 100, 200, 200): {}'.format(g)

        # Ensure we hit max size
        self.click_and_drag('BTN_MIDDLE', 275, 200, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(100, 100, 300, 300, g):
            return wt.Status.WRONG, 'geometry mismatch after BR ratio resize to (100, 100, 300, 300): {}'.format(g)

        self.click_and_drag('BTN_MIDDLE', 101, 101, 1000, 1000)
        self.wait_for_clients()
        g = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(350, 350, 50, 50, g):
            return wt.Status.WRONG, 'geometry mismatch after TL resize to (350, 350, 50, 50): {}'.format(g)

        return wt.Status.OK, None
