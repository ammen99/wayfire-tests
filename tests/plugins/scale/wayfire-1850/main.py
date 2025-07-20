#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1850
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=2)

        weston_focus = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['activated']

        # toggle scale
        self.socket.press_key('KEY_Z')
        self.socket.press_key('KEY_Z')

        focus_now = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['activated']
        if focus_now != weston_focus:
            return wt.Status.WRONG, 'weston-terminal changed focus: ' + str(focus_now)

        return wt.Status.OK, None
