#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This test maximizes and unmaximimzes a gtk4 client, then moves it with titlebar drag.
# It checks that the window does not jump when dragged. See this commit for more info:
# https://github.com/WayfireWM/wayfire/commit/2aeaf21e22fd13b1034ab6b24305d6b33fa6bf87
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk4-demo', 'wf-panel'])

    def _run(self):
        print("\n")
        self.socket.run('gtk4-demo')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients(5)

        gtk4_demo_view_info = self.socket.get_view_info("org.gtk.Demo4")
        geometry1 = gtk4_demo_view_info["base-geometry"]
        self.wait_for_clients(1)

        self.socket.sock.assign_slot(gtk4_demo_view_info["id"], "slot_c")
        self.wait_for_clients(15)
        self.socket.sock.assign_slot(gtk4_demo_view_info["id"], "restore")
        self.wait_for_clients(10)

        self.socket.move_cursor(450, 125)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        self.socket.move_cursor(500, 125)
        self.wait_for_clients(2)
        self.socket.move_cursor(550, 125)
        self.wait_for_clients(2)
        self.socket.move_cursor(500, 125)
        self.wait_for_clients(2)
        self.socket.move_cursor(450, 125)
        self.wait_for_clients(2)
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(1)

        gtk4_demo_view_info = self.socket.get_view_info("org.gtk.Demo4")
        geometry2 = gtk4_demo_view_info["base-geometry"]
        self.wait_for_clients(1)

        if geometry1["x"] != geometry2["x"] or geometry1["y"] != geometry2["y"]:
            return wt.Status.WRONG, "Geometry incorrect, should be the same position before move.\nNOTE: x1: " + \
                str(geometry1["x"]) + " x2: " + str(geometry2["x"]) + " - y1: " + str(geometry1["y"]) + " y2: " + str(geometry2["y"])

        return wt.Status.OK, None
