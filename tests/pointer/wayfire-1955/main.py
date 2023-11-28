#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

# Wayfire #1955
# The problem is a dialog that we open at runtime.
# First, the dialog is mapped as a normal window so it may receive a pointer.enter event.
# Then, its parent is set to the main window and it is moved, triggering GEOMETRY scene update.
# This should cause Wayfire to re-send a motion event.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer dialog-shortcut emit-enter-coords')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.move_cursor(200, 200)
        self.wait_for_clients(2)

        self.socket.press_key('KEY_O') # Open dialog
        self.wait_for_clients_to_open(nr_clients=2,waits=20)
        self.wait_for_clients(2)

        info = self.socket.get_view_info_title('TestDialog')
        Ex = 200 - info['bbox']['x']
        Ey = 200 - info['bbox']['y']
        last_line = gtk.skip_to_last_line()
        if last_line != f"pointer-enter-dialog {Ex},{Ey}" and last_line != f"dialog-pointer-motion {Ex},{Ey}":
            return wt.Status.WRONG, f'Dialog expected {Ex},{Ey} but got: {last_line}'

        return wt.Status.OK, None
