#!/bin/env python3

import wftest as wt
import wfipclib as wi
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('xterm'):
            return wt.Status.SKIPPED, "xterm binary not found in $PATH"
        return wt.Status.OK, None

    def _run(self):
        # Add panel to reproduce #2585
        self.run_get_id('wf-panel -c wf-shell.ini')
        self.socket.run('xterm -fullscreen')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_for_clients(2) # fullscreening

        xterm = self.socket.get_view_info('XTerm')
        if not xterm:
            return wt.Status.WRONG, 'No xterm running?'

        if not wi.check_geometry(0, 0, 504, 657, xterm['base-geometry']) or \
                not wi.check_geometry(0, 0, 504, 657, xterm['geometry']):
            return wt.Status.WRONG, "xterm has wrong fullscreen size {}!".format(xterm['base-geometry'])
        return wt.Status.OK, None
