#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test starts scale and checks that it works with touch gestures and can exit with touch input
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_special'])

    def _run(self):
        # Open a dialog to also test Wayfire #2447
        self.socket.run('gtk_special a b')
        self.wait_for_clients_to_open(nr_clients=2)

        # Pinch-in gesture
        self.socket.set_touch(0, 0, 0)
        self.socket.set_touch(1, 500, 500)
        self.socket.set_touch(0, 249, 249)
        self.socket.set_touch(1, 251, 251)
        self.socket.release_touch(0)
        self.socket.release_touch(1)
        self.wait_for_clients(2)

        if error := self.take_screenshot('1-scale-start'):
            return wt.Status.CRASHED, error

        # Click in the middle to select weston-terminal
        self.socket.set_touch(0, 250, 250)
        self.socket.release_touch(0)
        self.wait_for_clients(2)

        if error := self.take_screenshot('2-scale-exited'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
