#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This test maximizes a client, then moves it with titlebar drag to test for correct snapoff.
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

        self.socket.move_cursor(450, 100)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        self.socket.move_cursor(450, 125)
        self.wait_for_clients(2)
        self.socket.move_cursor(450, 150)
        self.wait_for_clients(2)
        self.socket.move_cursor(450, 175)
        self.wait_for_clients(2)
        self.socket.move_cursor(450, 200)
        self.wait_for_clients(2)
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(1)

        gtk4_demo_view_info = self.socket.get_view_info("org.gtk.Demo4")
        geometry2 = gtk4_demo_view_info["base-geometry"]
        self.wait_for_clients(1)

        if geometry1["width"] != geometry2["width"] or geometry1["height"] != geometry2["height"]:
            return wt.Status.WRONG, "Geometry incorrect, should be the same size after move drag snapoff.\nNOTE: width1: " + \
                str(geometry1["width"]) + " width2: " + str(geometry2["x"]) + " - height1: " + str(geometry1["height"]) + " height2: " + str(geometry2["height"])

        return wt.Status.OK, None
