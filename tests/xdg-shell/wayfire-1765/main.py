#!/bin/env python3

import wftest as wt
import importlib

def is_gui() -> bool:
    return False

# Wayfire 1765, gtk popup flickering
class WTest(wt.WayfireTest):
    def prepare(self):
        spec = importlib.util.find_spec('gi') # type: ignore
        if spec:
            import gi
            try:
                gi.require_version("Gtk", "3.0")
                return wt.Status.OK, None
            except:
                return wt.Status.SKIPPED, 'gi.GTK missing'
        else:
            return wt.Status.SKIPPED, 'gi missing'

    def _view_ids(self):
        views = self.socket.list_views()
        ids = []
        for v in views:
            ids.append(v['id'])
        return sorted(ids)

    def _run(self):
        self.socket.run('python3 client.py')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.move_cursor(20, 40)

        # Try to wait for the first popup. If it does not flicker, we will 'catch it'
        if not self.wait_for_clients_to_open(nr_clients=2, interval=16, waits=60):
            return wt.Status.WRONG, 'Popups flicker 1?'

        # If we caught a flickering popup, it might immediately go away => check again
        start_ids = self._view_ids()
        if len(start_ids) != 2:
            return wt.Status.WRONG, 'Popups flicker 2?'

        self.wait_ms(400)

        # Finally, if popup does not flicker, it should still be open after all this time
        end_ids = self._view_ids()
        if start_ids != end_ids:
            return wt.Status.WRONG, 'Popups flicker 3?'

        return wt.Status.OK, None
