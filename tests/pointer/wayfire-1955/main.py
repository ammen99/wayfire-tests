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
        #gtk = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'pointer dialog-shortcut emit-enter-coords &> /tmp/log')
        #self.wait_for_clients_to_open(nr_clients=1)

        #layout = {}
        #layout['gtk1'] = (100, 100, 400, 400)
        #self.socket.layout_views(layout)
        #self.wait_for_clients(20)

        self.socket.run('geany')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.move_cursor(300, 300)

        try:
            self.wait_for_clients(20)

            self.socket.press_key('C-KEY_O') # Open dialog
            self.wait_for_clients_to_open(nr_clients=2, waits=20)
            self.wait_for_clients(20)

        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
