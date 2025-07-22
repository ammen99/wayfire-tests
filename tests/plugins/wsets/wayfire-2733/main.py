#!/bin/env python3

import wftest as wt
from wayfire.extra.ipc_utils import WayfireUtils
from random import randint, choice

def is_gui() -> bool:
    return False

# This test spams kitty terminal on two different outputs and moves terminals between outputs with wsets
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['kitty'])

    def _run(self):
        self.socket.create_wayland_output()
        utils = WayfireUtils(self.socket.sock)

        # ensure at least one kitty for choice() to work
        self.run_get_id('kitty /bin/sh')
        for i in range(50):
            if i % 5 == 0:
                self.socket.run('kitty /bin/sh')

            cursor_pos_x, cursor_pos_y = self.socket.sock.get_cursor_position()
            self.socket.stipc.click_and_drag(
                "BTN_LEFT",
                cursor_pos_x,
                cursor_pos_y,
                randint(1, 100000),
                randint(1, 100000),
                release=True,
                steps=randint(10, 100),
            )

            views = self.socket.list_views()
            random_view_id = choice([view['id'] for view in views if view["role"] == "toplevel"])
            self.socket.sock.send_view_to_wset(random_view_id, randint(1, 2))
            self.socket.sock.set_focus(random_view_id)
            utils.center_cursor_on_view(random_view_id)

        return wt.Status.OK, None
