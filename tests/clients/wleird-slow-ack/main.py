#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

# Wayfire #1852
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-slow-ack-configure'])

    def _run(self):
        _, pid = self.run_get_id('wleird-slow-ack-configure 0 0') # default size 0, 0 means unmap on default size ...
        self.wait_ms(1000)

        if err := self.take_screenshot('1-map-unmap'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        layout = {}
        layout['wleird-slow-ack-configure'] = (100, 100, 300, 400)
        self.socket.layout_views(layout)
        self.wait_ms(200)

        # Configure unmapped view
        layout = {}
        layout['wleird-slow-ack-configure'] = (0, 0, 1000, 1000)
        self.socket.layout_views(layout)
        self.wait_ms(200)
        if err := self.take_screenshot('2-pending-resize'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        # Trigger the view again
        self.send_signal(pid, signal.SIGUSR1)

        self.wait_ms(500)
        if err := self.take_screenshot('3-client-driven-resize'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        return wt.Status.OK, None
