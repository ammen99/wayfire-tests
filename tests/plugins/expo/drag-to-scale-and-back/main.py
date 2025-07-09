#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout['org.freedesktop.weston.wayland-terminal'] = (0, 0, 500, 500, 'WL-1')
        layout['gcs'] = (0, 0, 500, 500, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Focus WL-1 and start expo
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.press_key('KEY_E')

        # Focus WL-2 and start scale
        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.press_key('KEY_S')


        self.wait_for_clients(2)
        if error := self.take_screenshot('1-start-expo-and-scale'):
            return wt.Status.CRASHED, error

        # Drag weston-terminal from WL-1 to WL-2
        self.click_and_drag('BTN_LEFT', 125, 125, 750, 250, release=False) # Middle of WL-1/workspace 1,1 to middle of WL-2
        self.wait_ms(400) # 300ms hardcoded scaling animation

        if error := self.take_screenshot('2-dragged-to-wl2'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        if error := self.take_screenshot('3-both-on-wl2'):
            return wt.Status.CRASHED, error

        self.click_and_drag('BTN_LEFT', 625, 250, 125, 125, release=False) # Drag from WL-2 to WL-1
        self.wait_ms(400) # 300ms hardcoded scaling animation
        if error := self.take_screenshot('4-dragged-to-wl1'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        if error := self.take_screenshot('5-dropped-on-expo'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'full') # Exit expo
        self.wait_for_clients()
        if error := self.take_screenshot('6-expo-exited'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
