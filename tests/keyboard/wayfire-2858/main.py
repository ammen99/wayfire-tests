#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #2858: ensure that when minimizing a window and the focus is transferred to a layer-shell surface,
# the window still loses activated status.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wleird-layer-shell'])

    def get_subtests(self):
        return [('bg', 'background'), ('top', 'top')]

    def _run(self):
        # Start keylogger
        id, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        self.run_get_id(f'wleird-layer-shell -l {self.subtest_data} -k exclusive')

        if self.socket.get_view_info_id(id)['activated'] is not True:
            return wt.Status.WRONG, 'Terminal is not activated after launch!'

        assert isinstance(id, int)
        self.socket.sock.set_view_minimized(id, True)
        self.wait_for_clients(2)

        if self.socket.get_view_info_id(id)['activated'] is True:
            return wt.Status.WRONG, 'Terminal is still activated after minimizing!'

        return wt.Status.OK, None
