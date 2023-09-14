#!/bin/env python3

import wftest as wt

def sensitivity() -> float:
    # We want high sensitivity since gcs is gray by default
    return 1

def is_gui() -> bool:
    return True

# Wayfire #1886
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.run('gtk_color_switcher')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['gtk_color_switcher'] = (150, 50, 200, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        self.click_and_drag('BTN_LEFT', 250, 300, 300, 250)

        layout['gtk_color_switcher'] = (200, 100, 200, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        layout['gtk_color_switcher'] = (250, 150, 200, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        layout['gtk_color_switcher'] = (300, 200, 200, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        if err := self.take_screenshot('1-no-artifacts'):
            return wt.Status.CRASHED, 'Failed to take screenshot: ' + str(err)

        return wt.Status.OK, None
