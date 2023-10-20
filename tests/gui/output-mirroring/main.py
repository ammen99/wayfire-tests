#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

# Checks that output mirroring basics work
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.create_wayland_output()
        self.wait_ms(100)

        if error := self.take_screenshot('1-mirror-setup'):
            return wt.Status.CRASHED, error

        pid = self.socket.run('gtk_color_switcher gcs')['pid']
        self.wait_for_clients_to_open(nr_clients=1)

        if error := self.take_screenshot('2-mirror-client'):
            return wt.Status.CRASHED, error

        self.send_signal(pid, signal.SIGUSR1)
        self.wait_for_clients(2)

        if error := self.take_screenshot('3-mirror-update'):
            return wt.Status.CRASHED, error

        # Unfortunately, we can't take a screenshot because of animation, so we just
        # wait to make sure Wayfire doesn't crash
        return wt.Status.OK, None
