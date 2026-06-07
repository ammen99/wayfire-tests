#!/bin/env python3

import wftest as wt
import imageio
import signal

def is_gui() -> bool:
    return False

# Makes sure that wm-actions sets the output region correctly
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.create_wayland_output()

        # focus wl-1
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')

        # run gcs on the right workspace, make it always-on-top
        self.socket.sock.set_workspace(1, 0)
        id, pid = self.run_get_id('gtk_color_switcher')
        self.send_signal(pid, signal.SIGUSR1)
        self.socket.sock.set_view_always_on_top(id, True) #type: ignore
        self.wait_for_clients()

        # gcs is now on the 'right' of us, which overlaps with wl-2
        # if limit region is set correctly, however, the view won't be visible on wl-2
        self.socket.sock.set_workspace(0, 0)

        if err := self.take_screenshot('setup'):
            return wt.Status.CRASHED, "Failed to take screenshot " + err

        img = imageio.imread(self.screenshots[0])
        if img.any():
            return wt.Status.WRONG, "Background is not black, max value is {}".format(img.max())

        return wt.Status.OK, None
