#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Open x11_map_unmap on the non-focused output => it should be reconfigured on the current output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_map_unmap'])

    def _run(self):
        # Create WL-2
        self.socket.create_wayland_output()

        # Click and focus on WL-1
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')

        self.socket.run('x11_map_unmap -a x11 -x 800 -y 200 -w 200 -h 300 -r 0') # Geometry on WL-2
        self.wait_for_clients_to_open(nr_clients=1)

        if err := self.take_screenshot('other-output'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        return wt.Status.OK, None
