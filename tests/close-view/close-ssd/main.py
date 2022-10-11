#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        self.socket.run('gtk_logger gtk1 /tmp/gtk1')
        self.wait_for_clients(2)

        layout = {}
        layout['gtk1'] = (100, 200, 400, 300)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        if len(self.socket.list_views()) != 1:
            return wt.Status.WRONG, "Not all views are open? " + str(self.socket.list_views())

        self.socket.move_cursor(490, 210)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        if len(self.socket.list_views()) > 0:
            return wt.Status.WRONG, "gtk-logger is still open" + str(self.socket.list_views())

        return wt.Status.OK, None
