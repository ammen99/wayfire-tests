#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def run(self, *args, **kwargs):
        # Make sure WL-1 is enabled when starting wayfire
        shutil.copyfile('wl1-enabled.ini', 'wayfire.ini')
        return super().run(*args, **kwargs)

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.create_wayland_output()
        shutil.copyfile('wl1-disabled.ini', 'wayfire.ini')
        self.wait_for_clients(2)
        if not self.socket.ping():
            return wt.Status.CRASHED, 'Wayfire crashed after disabling?'

        shutil.copyfile('wl1-enabled.ini', 'wayfire.ini')
        self.wait_for_clients(2)
        if not self.socket.ping():
            return wt.Status.CRASHED, 'Wayfire crashed after enabling?'

        return wt.Status.OK, None
