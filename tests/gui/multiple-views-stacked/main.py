#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('wleird-cursor'):
            return wt.Status.SKIPPED, "Missing wleird-cursor (Did you compile wleird test clients?)"
        if not shutil.which('wleird-gamma-blend'):
            return wt.Status.SKIPPED, "Missing wleird-gamma-blend (Did you compile wleird test clients?)"
        if not shutil.which('wleird-layer-shell'):
            return wt.Status.SKIPPED, "Missing wleird-layer-shell (Did you compile wleird test clients?)"
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('wleird-layer-shell -l bottom -a bottom -w 500 -h 500 -c green')
        self.socket.run('wleird-layer-shell -l top -a left -c blue')
        self.socket.run('wleird-layer-shell -l top -a right -c red')
        self.socket.run('wleird-gamma-blend')
        self.wait_for_clients(2) # Wait for gamma-blend to start
        self.socket.run('wleird-cursor')
        self.wait_for_clients(2) # Wait for cursor to start

        layout = {}
        layout['wleird-cursor'] = (0, 0, 100, 100)
        layout['wleird-gamma-blend'] = (50, 50, 400, 400)
        self.socket.layout_views(layout)
        self.socket.move_cursor(90, 90)
        self.wait_for_clients(2)

        return wt.Status.OK, None
