#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test opens gcs and weston-terminal on two outputs, starts scale and drags the window to the scale-active-output.
# Then it tries to maximize the dragged view, which should be dropped to scale instead.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('weston-terminal')
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients(2)

        layout = {}
        layout['gcs'] = (0, 0, 500, 500, 'WL-1')
        layout['nil'] = (0, 0, 500, 500, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Focus WL-1 and start scale
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.press_key('KEY_S')

        # Focus WL-2 and drag weston-terminal to WL-1
        self.click_and_drag('BTN_LEFT', 750, 5, 250, 0, release=True)

        self.wait_for_clients(200)
 #       if error := self.take_screenshot('1-start-expo-and-scale'):
 #           return wt.Status.CRASHED, error

 #       # Drag weston-terminal from WL-1 to WL-2
 #       self.click_and_drag('BTN_LEFT', 125, 125, 750, 250, release=False) # Middle of WL-1/workspace 1,1 to middle of WL-2
 #       self.wait_ms(400) # 300ms hardcoded scaling animation

 #       if error := self.take_screenshot('2-dragged-to-wl2'):
 #           return wt.Status.CRASHED, error

 #       self.socket.click_button('BTN_LEFT', 'release')
 #       self.wait_for_clients()
 #       if error := self.take_screenshot('3-both-on-wl2'):
 #           return wt.Status.CRASHED, error

 #       self.click_and_drag('BTN_LEFT', 625, 250, 125, 125, release=False) # Drag from WL-2 to WL-1
 #       self.wait_ms(400) # 300ms hardcoded scaling animation
 #       if error := self.take_screenshot('4-dragged-to-wl1'):
 #           return wt.Status.CRASHED, error

 #       self.socket.click_button('BTN_LEFT', 'release')
 #       self.wait_for_clients()
 #       if error := self.take_screenshot('5-dropped-on-expo'):
 #           return wt.Status.CRASHED, error

 #       self.socket.click_button('BTN_LEFT', 'full') # Exit expo
 #       self.wait_for_clients()
 #       if error := self.take_screenshot('6-expo-exited'):
 #           return wt.Status.CRASHED, error

        return wt.Status.OK, None
