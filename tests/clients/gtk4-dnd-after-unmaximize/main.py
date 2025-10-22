#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test maximizes and unmaximimzes a gtk4 client, then moves it with titlebar drag.
# It checks that the window does not jump when dragged. See this commit for more info:
# https://github.com/WayfireWM/wayfire/commit/2aeaf21e22fd13b1034ab6b24305d6b33fa6bf87
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk4-demo', 'wf-panel'])

    def _run(self):
        gtk4_id, _ = self.run_get_id('gtk4-demo')

        gtk4_demo_view_info = self.socket.get_view_info_id(gtk4_id)
        geometry1 = gtk4_demo_view_info["base-geometry"]

        self.socket.sock.assign_slot(gtk4_id, "slot_c") # type: ignore
        self.wait_for_clients(4)
        self.socket.sock.assign_slot(gtk4_id, "restore") # type: ignore
        self.wait_for_clients(4)

        sx = gtk4_demo_view_info["bbox"]["x"] + gtk4_demo_view_info["bbox"]["width"] / 2
        sy = gtk4_demo_view_info["bbox"]["y"] + 25

        self.socket.move_cursor(sx, sy)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        self.socket.move_cursor(sx + 50, sy)
        self.wait_for_clients(2)
        self.socket.move_cursor(sx + 100, sy)
        self.wait_for_clients(2)
        self.socket.move_cursor(sx + 50, sy)
        self.wait_for_clients(2)
        self.socket.move_cursor(sx, sy)
        self.wait_for_clients(2)
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(1)

        gtk4_demo_view_info = self.socket.get_view_info_id(gtk4_id)
        geometry2 = gtk4_demo_view_info["base-geometry"]
        if geometry1["x"] != geometry2["x"] or geometry1["y"] != geometry2["y"]:
            return wt.Status.WRONG, "Geometry incorrect, should be the same position before move.\nNOTE: x1: " + \
                str(geometry1["x"]) + " x2: " + str(geometry2["x"]) + " - y1: " + str(geometry1["y"]) + " y2: " + str(geometry2["y"])

        return wt.Status.OK, None
