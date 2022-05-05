#!/bin/env python3

import wftest as wt
import wfipclib as wi
import shutil
import time

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('xterm'):
            return wt.Status.SKIPPED, "xterm binary not found in $PATH"
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('xterm -fullscreen')
        time.sleep(0.2) # Wait for xterm to start

        xterm = self.socket.get_view_info('XTerm')
        if not xterm:
            return wt.Status.WRONG, 'No xterm running?'

        if not wi.check_geometry(0, 0, 504, 657, xterm['base-geometry']) or \
                not wi.check_geometry(0, 0, 504, 657, xterm['geometry']):
            return wt.Status.WRONG, "xterm has wrong fullscreen size {}!".format(xterm['base-geometry'])
        return wt.Status.OK, None
