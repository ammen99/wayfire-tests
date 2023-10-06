#!/bin/env python3

import wfutil as wu
import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Wayfire #1908
# This test opens gtk_color_switcher on the workspace below and starts scale with all workspaces.
# Then, it sends SIGUSR1 so that gcs changes its color.
# The expected visual result is that gcs has its new color.

# Note: we need an animation, so that the initial animation frame, gcs is still invisible.

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        gcs = wu.LoggedProcess(self.socket, 'gtk_color_switcher', 'gcs')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['gcs'] = (400, 900, 100, 100) # bottom-right corner of workspace below, ensuring it is not visible in the beginning of the animation
        self.socket.layout_views(layout)
        self.wait_for_clients(3)

        self.socket.press_key('KEY_T')
        self.wait_ms(150) # Wait for animation

        gcs.reset_logs()
        self.send_signal(gcs.pid, signal.SIGUSR1);
        self.wait_for_clients(2)

        try:
            gcs.expect_line_throw('signal-draw')
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
