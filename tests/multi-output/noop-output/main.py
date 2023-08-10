#!/bin/env python3

import wfipclib as wi
import wftest as wt
import os
import signal

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher', 'wf-background'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        pid = self.socket.run('gtk_color_switcher cs')["pid"]
        self.socket.run('wf-background')
        self.wait_for_clients(4)
        if self._get_views() != ['cs', 'layer-shell']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['cs'] = (10, 10, 400, 400, 'WL-1') # Overlaps the left half of WL-2
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.destroy_wayland_output('WL-1')
        self.wait_for_clients(2)
        if self._get_views() != ['cs', 'layer-shell']:
            return wt.Status.WRONG, 'Demo app crashed after destroying WL-1: ' + str(self._get_views())

        # Check that view was scaled to match the NOOP-1 resolution
        cs_geometry = self.socket.get_view_info_title('cs')["geometry"]
        if not wi.check_geometry(5, 5, 200, 200, cs_geometry):
            return wt.Status.WRONG, 'Demo app has wrong size on NOOP-1: ' + str(cs_geometry)

        # Trigger damage, move cursor, any action to see that wayfire can handle it
        os.kill(pid, signal.SIGUSR1)
        self.socket.move_cursor(10, 10)
        self.wait_for_clients(2)
        if self._get_views() != ['cs', 'layer-shell']:
            return wt.Status.WRONG, 'Demo app crashed after playing around with NOOP-1: ' + str(self._get_views())

        self.socket.create_wayland_output()
        self.wait_ms(1200) # We have to wait quite a long time for everything to settle down,
        # as for example NOOP-1 is not destroyed immediately to avoid races in wayland.
        # Currently, the timer is set to 1s in Wayfire.

        # Check that view was scaled to match the WL-2 resolution
        if self._get_views() != ['cs', 'layer-shell']:
            return wt.Status.WRONG, 'Demo app crashed after restoring to WL-2: ' + str(self._get_views())

        cs_geometry = self.socket.get_view_info_title('cs')["geometry"]
        if not wi.check_geometry(10, 10, 400, 400, cs_geometry):
            return wt.Status.WRONG, 'Demo app has wrong size after restoring to WL-2: ' + str(cs_geometry)

        return wt.Status.OK, None
