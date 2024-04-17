#!/bin/env python3

import wftest as wt
import signal
import traceback
import os

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['xterm'])

    def run_once(self, wayfire_path: str, log: str):
        try:
            self.run_wayfire(wayfire_path, log)
            self.socket.run('xterm')
            self.wait_for_clients_to_open(nr_clients=1)
            self.socket.destroy_wayland_output('WL-1')

            info = self.socket.list_views()[0]
            sx = info['bbox']['x'] + info['bbox']['width'] / 2
            sy = info['bbox']['y'] + info['bbox']['height'] / 2
            self.click_and_drag('BTN_LEFT', sx, sy, 500, 500)

            assert self._wayfire_process
            os.killpg(self._wayfire_gid, signal.SIGINT)
            if status := self._wayfire_process.wait(5.0):
                return wt.Status.CRASHED, "Wayfire process exited with status {}".format(status)

        except Exception as _:
            return wt.Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()

        return wt.Status.OK, None
