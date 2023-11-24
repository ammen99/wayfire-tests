#!/bin/env python3

import wftest as wt
from Xlib import display

def is_gui() -> bool:
    return True

# Open x11_map_unmap on the non-focused output => it should be reconfigured on the current output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_map_unmap'])

    def reconfigure(self, x: int, y: int, unmap: bool):
        disp = display.Display(self.socket.xwayland_display()['display'])
        root = disp.screen().root
        window_ids = root.query_tree().children
        for id in window_ids:
            window = disp.create_resource_object('window', id)
            if window.get_wm_name() == 'x11':
                if unmap:
                    window.unmap()
                    disp.sync()
                    self.wait_for_clients(2)

                window.configure(x=x, y=y)
                disp.sync()
                if unmap:
                    window.map()
                    disp.sync()
                    self.wait_for_clients(2)

        disp.close()

    def _run(self):
        # Create WL-2
        self.socket.create_wayland_output()

        # Click and focus on WL-1
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')

        self.socket.run('x11_map_unmap -a x11 -x 800 -y 200 -w 200 -h 300 -r 0 -o') # Geometry on WL-2
        self.wait_for_clients_to_open(nr_clients=1)

        if err := self.take_screenshot('1-on-wl2'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.reconfigure(600, 100, False)
        self.wait_for_clients()
        if err := self.take_screenshot('2-move-on-wl2'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.reconfigure(100, 100, False)
        self.wait_for_clients()
        if err := self.take_screenshot('3-move-on-wl1'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        self.reconfigure(700, 150, True)
        self.wait_for_clients(2)
        if err := self.take_screenshot('4-remap-wl2'):
            return wt.Status.CRASHED, "Failed screenshot: ", str(err)

        return wt.Status.OK, None
