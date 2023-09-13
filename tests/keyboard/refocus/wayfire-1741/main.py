#!/bin/env python3

import wftest as wt
import wfutil as wu
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-layer-shell', 'gtk_logger'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def run(self, *args, **kwargs):
        # Make sure WL-1 is disabled when starting wayfire
        shutil.copyfile('wl1-disabled.ini', 'wayfire.ini')
        return super().run(*args, **kwargs)

    def _run(self):
        # Grab exclusive keyboard focus on the NOOP output
        self.socket.run('wleird-layer-shell -k exclusive -l overlay')
        self.wait_for_clients_to_open(nr_clients=1)

        shutil.copyfile('wl1-enabled.ini', 'wayfire.ini')
        self.wait_for_clients(2)
        if not self.socket.ping():
            return wt.Status.CRASHED, 'Wayfire crashed after enabling?'

        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_ms(1100) # for noop to be destroyed

        try:
            gtk.expect_line_throw("keyboard-enter")
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
