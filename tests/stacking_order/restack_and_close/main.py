#!/bin/env python3

import wftest as wt
import wfipclib as wi
import shutil
import time

def is_gui() -> bool:
    return False

# This test opens three special clients which all overlap in the same area ((50, 50) to (100, 100))
# They are focused one by one by clicking on them.
# Then, they are closed one by one by right clicking on them.
# The order in which they are closed needs to reflect the stacking order created
# by the left clicks.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('x11_click_to_close'):
            return wt.Status.SKIPPED, "Did you compile test clients?"
        return wt.Status.OK, None

    def _run(self):
        self.socket.run('x11_click_to_close 1 0 0 100 100 > /tmp/a');
        self.socket.run('x11_click_to_close 2 50 50 100 100 > /tmp/b');
        self.socket.run('x11_click_to_close 3 0 50 100 100 > /tmp/c');
        time.sleep(1) # Wait for clients to start

        # Bring 3 to front
        self.socket.move_cursor(1, 140)
        self.socket.click_button('BTN_LEFT', 'full')
        time.sleep(1)

        # Bring 1 to front
        self.socket.move_cursor(1, 1)
        self.socket.click_button('BTN_LEFT', 'full')
        time.sleep(1)

        # Bring 2 to front
        self.socket.move_cursor(140, 140)
        self.socket.click_button('BTN_LEFT', 'full')
        time.sleep(1)

        # Close windows one by one by clicking on the shared area
        self.socket.move_cursor(75, 75)
        self.socket.click_button('BTN_RIGHT', 'full')
        time.sleep(0.2)
        time.sleep(1) # Wait for clients to start
        views = sorted([v['app-id'] for v in self.socket.list_views()])
        print(views)
        self.socket.click_button('BTN_RIGHT', 'full')
        time.sleep(0.2)
        views = sorted([v['app-id'] for v in self.socket.list_views()])
        print(views)
        self.socket.click_button('BTN_RIGHT', 'full')
        time.sleep(2)
        views = sorted([v['app-id'] for v in self.socket.list_views()])
        print(views)
        print("DONE")
        time.sleep(1000)

        #xterm = self.socket.get_view_info('XTerm')
        #if not xterm:
        #    return wt.Status.WRONG, 'No xterm running?'

        #if not wi.check_geometry(0, 0, 504, 657, xterm['base-geometry']) or \
        #        not wi.check_geometry(0, 0, 504, 657, xterm['geometry']):
        #    return wt.Status.WRONG, "xterm has wrong fullscreen size {}!".format(xterm['base-geometry'])
        return wt.Status.OK, None
