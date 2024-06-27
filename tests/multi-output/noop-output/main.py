#!/bin/env python3

import wfipclib as wi
import wftest as wt
import signal

def is_gui() -> bool:
    return True

# Test that everything works with the noop output
# Also test Wayfire #2212

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher', 'wf-background', 'wleird-wfshell-tester'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        pid_tester = self.socket.run('wleird-wfshell-tester')["pid"]
        pid = self.socket.run('gtk_color_switcher cs')["pid"]
        self.socket.run('wf-background')
        self.wait_for_clients_to_open(nr_clients=2)

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
        if not wi.check_geometry(0, 0, 250, 250, cs_geometry):
            return wt.Status.WRONG, 'Demo app has wrong size on NOOP-1: ' + str(cs_geometry)

        # Trigger damage, move cursor, any action to see that wayfire can handle it
        self.send_signal(pid, signal.SIGUSR1)
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
        if not wi.check_geometry(0, 0, 250, 250, cs_geometry):
            return wt.Status.WRONG, 'Demo app has wrong size after restoring to WL-2: ' + str(cs_geometry)

        if err := self.take_screenshot('1-final'):
            return wt.Status.WRONG, "Failed to take screenshot: " + str(err)

        # Make sure cleaning up resources is ok
        self.send_signal(pid_tester, signal.SIGKILL)
        self.wait_for_clients(2)

        return wt.Status.OK, None
