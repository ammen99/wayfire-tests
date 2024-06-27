#!/bin/env python3

import traceback
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['glxgears', 'weston-terminal', 'wleird-layer-shell'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def run_once(self, wayfire_path: str, log: str):
        try:
            self.run_wayfire(wayfire_path, log)
            self.socket.run('glxgears')
            self.socket.run('weston-terminal --shell=/bin/sh')
            self.socket.run('weston-terminal --shell=/bin/sh')
            self.socket.run('wleird-layer-shell -l top')
            self.wait_for_clients_to_open(nr_clients=6)

            self.socket.set_key_state('KEY_LEFTCTRL', True)
            self.socket.set_key_state('KEY_LEFTALT', True)
            self.socket.set_key_state('KEY_BACKSPACE', True)
            assert self._wayfire_process
            if status := self._wayfire_process.wait(1.0):
                return wt.Status.CRASHED, "Wayfire process exited with status {}".format(status)

        except Exception as _:
            return wt.Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()

        return wt.Status.OK, None
