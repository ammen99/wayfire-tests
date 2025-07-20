#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients_to_open(nr_clients=2)

        # Potentially wait for resize
        self.wait_for_clients(2)

        info = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)
        if not wi.check_geometry(0, 200, 1280, 520, info['geometry']):
            return wt.Status.WRONG, 'weston-terminal has invalid geometry: ' + str(info['geometry'])

        return wt.Status.OK, None
