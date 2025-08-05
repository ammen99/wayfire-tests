#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test maximizes a client, then moves it with titlebar drag to test for correct snapoff.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk4-demo'])

    def _run(self):
        id, _ = self.run_get_id('gtk4-demo')
        gtk4_demo_view_info = self.socket.get_view_info_id(id)
        geometry1 = gtk4_demo_view_info["base-geometry"]

        self.socket.sock.assign_slot(id, "slot_c") # type: ignore
        self.wait_for_clients(4)

        sx, sy = 640, 15
        self.click_and_drag('BTN_LEFT', sx, sy, sx, sy + 100, pause=50)
        self.wait_for_clients(2)

        gtk4_demo_view_info = self.socket.get_view_info_id(id) # type: ignore
        geometry2 = gtk4_demo_view_info["base-geometry"]
        self.wait_for_clients(1)

        if geometry1["width"] != geometry2["width"] or geometry1["height"] != geometry2["height"]:
            return wt.Status.WRONG, "Geometry incorrect, should be the same size after move drag snapoff.\nNOTE: width1: " + \
                str(geometry1["width"]) + " width2: " + str(geometry2["x"]) + " - height1: " + str(geometry1["height"]) + " height2: " + str(geometry2["height"])

        return wt.Status.OK, None
