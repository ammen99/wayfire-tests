#!/bin/env python3

import signal
import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        id, pid = self.run_get_id('gtk_color_switcher')
        layout = {}
        layout[id] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGKILL)
        self.socket.press_key('KEY_E')

        self.socket.move_cursor(50, 50)
        self.click_and_drag('BTN_LEFT', 50, 50, 250, 250)

        info = self.socket.get_view_info_id(id)
        if info and not wi.check_geometry(0, 0, 500, 500, info['bbox']):
            return wt.Status.WRONG, 'Wrong geometry ' + str(info)

        return wt.Status.OK, None
