#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens a layer-shell client on top and overlay layers, and proceeds
# to check that a fullscreen view is positioned between them.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-layer-shell', 'terminator'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('wleird-layer-shell -l top -c red')
        self.socket.run('wleird-layer-shell -l overlay -a bottom -c green')
        self.socket.run('terminator')
        self.wait_for_clients(4) # Wait a bit more, terminator is slow sometimes
        self.socket.press_key('KEY_F11')
        self.wait_for_clients(2)
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
