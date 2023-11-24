#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Check that when a workspace set is cleaned up, tile does not cause a crash.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        # Go to wset 2 and initialize the simple-tile state for it by opening a client
        self.socket.press_key('KEY_2')
        pid = self.socket.run('gtk_color_switcher a')['pid']
        self.wait_for_clients_to_open(nr_clients=1)

        # Close the client
        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients()

        # Go to wset 1 => wset 2 should be cleaned up
        self.socket.press_key('KEY_1')
        self.wait_for_clients()

        if views := self.socket.list_views():
            return wt.Status.WRONG, 'There are still views open! ' + str(views)

        # All is OK if wayfire has survied
        return wt.Status.OK, None
