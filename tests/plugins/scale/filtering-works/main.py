#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('gtk_color_switcher gcs')["pid"]
        self.wait_for_clients_to_open(nr_clients=2)

        self.socket.press_key('KEY_T')
        self.wait_for_clients()

        if error := self.take_screenshot('1-scale-start'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_Z')
        self.socket.press_key('KEY_X')
        self.socket.press_key('KEY_C')
        self.wait_for_clients()

        if error := self.take_screenshot('2-scale-filter-hide-all'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_BACKSPACE')
        self.socket.press_key('KEY_BACKSPACE')
        self.socket.press_key('KEY_BACKSPACE')
        self.wait_for_clients()

        if error := self.take_screenshot('3-show-all-again'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_T')
        self.wait_for_clients()

        if error := self.take_screenshot('4-scale-exited'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
