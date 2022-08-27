#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-cursor', 'wleird-gamma-blend', 'wleird-layer-shell'])

    def _run(self):
        self.socket.run('wleird-layer-shell -l bottom -a bottom -w 500 -h 500 -c green')
        self.socket.run('wleird-layer-shell -l top -a left -c blue -w 250')
        self.socket.run('wleird-layer-shell -l top -a right -c red')
        self.socket.run('wleird-gamma-blend')
        self.wait_for_clients(2) # Wait for gamma-blend to start
        self.socket.run('wleird-cursor')
        self.wait_for_clients(2) # Wait for cursor to start

        layout = {}
        layout['wleird-cursor'] = (0, 0, 100, 100)
        layout['wleird-gamma-blend'] = (50, 50, 400, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        self.socket.move_cursor(240, 370) # bottom-right of blue layer-shell
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients(2)
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
