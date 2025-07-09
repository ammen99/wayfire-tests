#!/bin/env python3

import wftest as wt
import signal

# The test requires to compare two blur images.
# The blur effect is not very stable, so wide, but small
# changes are expected. Therefore, we need a higher sensitivity
# for this test.
def sensitivity():
    return 5.0

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-background'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        wt_pid = self.socket.run('weston-terminal --shell=/bin/sh')["pid"]
        self.socket.create_wayland_output()
        self.socket.run('wf-background')
        self.wait_ms(1500) # Wait for wf-background to start and be initialized

        if error := self.take_screenshot('clients-started'):
            return wt.Status.CRASHED, error

        layout = {}
        layout['org.freedesktop.weston.wayland-terminal'] = (0, 0, 500, 500, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(4)
        if error := self.take_screenshot('scene-setup'):
            return wt.Status.CRASHED, error

        self.socket.move_cursor(5, 5)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)

        if error := self.take_screenshot('start-drag'):
            return wt.Status.CRASHED, error

        self.socket.move_cursor(200, 200)
        self.wait_for_clients(2)
        if error := self.take_screenshot('in-flight'):
            return wt.Status.CRASHED, error

        self.send_signal(wt_pid, signal.SIGKILL)
        self.wait_for_clients(4)
        if error := self.take_screenshot('force-closed'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
