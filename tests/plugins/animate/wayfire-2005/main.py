#!/bin/env python3

import wftest as wt
import os
import signal
import shutil

def is_gui() -> bool:
    return False

# Wayfire #2005: ensure that animate can properly clean up views
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def run(self, *args, **kwargs):
        # Make sure animate is enabled
        shutil.copyfile('wayfire-animate.ini', 'wayfire.ini')
        return super().run(*args, **kwargs)

    def _run(self):
        pid = self.socket.run('weston-terminal')['pid']
        self.wait_for_clients_to_open(nr_clients=1)
        os.kill(pid, signal.SIGKILL)

        # Wait for weston-terminal to actually close
        self.wait_for_clients_to_open(nr_clients=0)

        # Disable animate plugin forcing it to clean up stuff
        shutil.copyfile('wayfire-no-animate.ini', 'wayfire.ini')
        self.wait_for_clients()

        if self.socket.list_views():
            return wt.Status.WRONG, 'weston-terminal still open!'

        return wt.Status.OK, None
