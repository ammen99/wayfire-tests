#!/bin/env python3

import wftest as wt
import wfipclib as wi
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        id, pid = self.run_get_id('gtk_color_switcher gcs')

        def configure(x, y, w, h):
            layout = {}
            layout[id] = (x, y, w, h)
            self.socket.layout_views(layout)
            self.wait_for_clients(2)

        configure(0, 0, 1000, 1000)
        self.send_signal(pid, signal.SIGKILL)
        configure(4000, 4000, 1000, 1000)

        g = self.socket.get_view_info_id(id)
        if not wi.check_geometry(4000, 4000, 1000, 1000, g['bbox']):
            return wt.Status.WRONG, 'geometry mismatch: {}'.format(g['bbox'])

        return wt.Status.OK, None
