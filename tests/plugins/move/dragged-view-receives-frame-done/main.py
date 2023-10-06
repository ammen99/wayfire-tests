#!/bin/env python3

import wftest as wt
import os
import signal

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        pid = self.socket.run('gtk_color_switcher gcs')["pid"]
        self.wait_for_clients(2)

        layout = {}
        layout['gcs'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(200, 200)

        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGUSR1)
        self.wait_for_clients(2)
        # Change color a second time. This forces gcs to wait for a frame done event
        self.send_signal(pid, signal.SIGUSR1)
        self.wait_for_clients(2)

        if error := self.take_screenshot('in-drag'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        self.send_signal(pid, signal.SIGUSR1)
        self.wait_for_clients(2)

        if error := self.take_screenshot('released'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
