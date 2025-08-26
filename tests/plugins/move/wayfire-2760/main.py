#!/bin/env python3

import signal
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        id1, pid1 = self.run_get_id('weston-terminal --shell=/bin/sh')
        id2, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        self.socket.create_wayland_output()

        layout = {}
        layout[id1] = (0, 0, 400, 400, 'WL-1')
        layout[id2] = (400, 0, 400, 400, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(200, 200)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        self.click_and_drag('BTN_RIGHT', 200, 200, 1300, 500, release=False, steps=10)
        self.socket.sock.set_focus(id2) # type: ignore
        self.send_signal(pid1, signal.SIGKILL)
        self.wait_for_clients(2)

        self.click_and_drag('BTN_RIGHT', 600, 200, 1300, 500, release=True, steps=10)
        self.wait_for_clients(2)

        info = self.socket.get_view_info_id(id2)
        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, f"Expected WL-2, got {info['output-name']}"

        return wt.Status.OK, None
