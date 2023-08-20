#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Wayfire #1852
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-slow-ack-configure'])

    def _run(self):
        self.socket.run('wleird-slow-ack-configure')
        self.wait_ms(1000)

        if err := self.take_screenshot('1-map-unmap'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        layout = {}
        layout['wleird-slow-ack-configure'] = (100, 100, 300, 400)
        self.socket.layout_views(layout)
        self.wait_ms(200)

        layout = {}
        layout['wleird-slow-ack-configure'] = (0, 0, 1000, 1000)
        self.socket.layout_views(layout)
        self.wait_ms(200)

        if err := self.take_screenshot('2-pending-resize'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.wait_ms(500)
        if err := self.take_screenshot('3-client-driven-resize'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        return wt.Status.OK, None
