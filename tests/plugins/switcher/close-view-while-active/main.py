#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher', 'weston-terminal'])

    def _run(self):
        wt_pid = self.socket.run('weston-terminal')['pid']
        self.wait_for_clients_to_open(nr_clients=1)
        gcs_pid = self.socket.run('gtk_color_switcher a')['pid']
        self.wait_for_clients_to_open(nr_clients=2)

        self.socket.press_key('KEY_N')
        if error := self.take_screenshot('1-switcher-active'):
            return wt.Status.CRASHED, error

        self.send_signal(wt_pid, signal.SIGKILL)
        self.wait_for_clients()

        if error := self.take_screenshot('2-switcher-active-one-fewer'):
            return wt.Status.CRASHED, error

        self.send_signal(gcs_pid, signal.SIGKILL)
        self.wait_for_clients()

        if error := self.take_screenshot('3-switcher-done'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
