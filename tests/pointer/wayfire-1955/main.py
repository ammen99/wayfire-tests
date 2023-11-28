#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# This test opens a special gtk client twice, then proceeds to move the pointer to test that the correct
# client receives motion events
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer dialog-shortcut emit-enter-coords &> /tmp/log')
        self.wait_for_clients_to_open(nr_clients=1)

        # position the views
        layout = {}
        layout['gtk1'] = (100, 100, 400, 400)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(300, 300) # Middle of gtk1

        self.socket.press_key('KEY_B') # move to workspace 2
        gtk.reset_logs()

        try:
            self.socket.press_key('KEY_A') # move back to workspace 1
            self.wait_for_clients(2)
            gtk.expect_line_throw('pointer-enter 200,200')

            self.socket.press_key('KEY_O') # Open dialog
            self.wait_for_clients_to_open(nr_clients=2)

            g = self.socket.get_view_info_title('TestDialog')
            gtk.expect_line_throw('pointer-leave')
            coord_x = 300 - g['bbox']['x']
            coord_y = 300 - g['bbox']['y']
            print(g['bbox'])
            print(g['geometry'])

            print(coord_x, coord_y)
            gtk.expect_line_throw(f'pointer-enter-dialog {coord_x},{coord_y}')
            gtk.expect_none_throw()
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
