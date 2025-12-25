#!/bin/env python3

import wftest as wt
import importlib

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        spec = importlib.util.find_spec('gi') # type: ignore
        if spec:
            import gi
            try:
                gi.require_version('Gtk', '3.0')
                gi.require_version('GtkLayerShell', '0.1')
            except:
                return wt.Status.SKIPPED, 'gi.GTK and/or gi.GtkLayerShell missing'

            from gi.repository import GtkLayerShell # type: ignore
            major = GtkLayerShell.get_major_version()
            minor = GtkLayerShell.get_minor_version()
            if major <= 0 and minor < 0.10:
                return wt.Status.SKIPPED, 'GtkLayerShell version < 0.10'
            return wt.Status.OK, None
        else:
            return wt.Status.SKIPPED, 'gi missing'

    def _run(self):
        self.socket.run('python3 client.py')
        self.wait_for_clients(4)
        # Wayfire crashes when the client opens in this bug scenario
        return wt.Status.OK, None
