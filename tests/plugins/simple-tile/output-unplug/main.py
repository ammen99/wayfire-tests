#!/bin/env python3

import wfipclib as wi
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('gtk_color_switcher cs')
        self.wait_for_clients(2)

        self.socket.destroy_wayland_output('WL-1')
        self.wait_for_clients(2)
        if self._get_views() != ['cs']:
            return wt.Status.WRONG, 'Demo app crashed after destroying WL-1: ' + str(self._get_views())

        self.socket.create_wayland_output()
        self.wait_ms(1200) # We have to wait quite a long time for everything to settle down,
        # as for example NOOP-1 is not destroyed immediately to avoid races in wayland.
        # Currently, the timer is set to 1s in Wayfire.

        # Check that view was scaled to match the WL-2 resolution
        if self._get_views() != ['cs']:
            return wt.Status.WRONG, 'Demo app crashed after restoring to WL-2: ' + str(self._get_views())

        cs_geometry = self.socket.get_view_info_title('cs')["geometry"]
        if not wi.check_geometry(0, 0, 600, 600, cs_geometry):
            return wt.Status.WRONG, 'Demo app has wrong size after restoring to WL-2: ' + str(cs_geometry)

        return wt.Status.OK, None
