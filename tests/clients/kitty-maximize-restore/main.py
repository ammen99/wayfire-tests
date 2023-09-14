#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1844: force kitty with CSD, maximize and restore it => the shadow subsurfaces should have correct size
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['kitty'])

    def _run(self):
        self.socket.run('WAYLAND_DEBUG=1 kitty &> /tmp/log')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['kitty'] = (100, 100, 300, 300)
        self.socket.layout_views(layout)
        self.wait_ms(600) # wait for kitty to resize and set the 'default' size
        bbox_begin = self.socket.get_view_info('kitty')['bbox']

        # Maximize kitty
        self.socket.move_cursor(250, 109) # kitty needs a motion event first to trigger move
        self.click_and_drag('BTN_LEFT', 250, 110, 250, 0)
        self.wait_ms(600) # wait so that kitty doesn't see this as a double-click

        self.socket.move_cursor(250, 4) # kitty needs a motion event first to trigger move
        self.click_and_drag('BTN_LEFT', 250, 5, 200, 200)
        self.wait_for_clients(2) # wait for kitty to adjust its size again

        bbox_end = self.socket.get_view_info('kitty')['bbox']
        if bbox_begin['width'] != bbox_end['width'] or bbox_begin['height'] != bbox_end['height']:
            return wt.Status.WRONG, f"kitty's bbox has incorrect size: start {bbox_begin}, now {bbox_end}"

        return wt.Status.OK, None
