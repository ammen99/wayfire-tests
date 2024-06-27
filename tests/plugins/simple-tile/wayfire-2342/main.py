#!/bin/env python3

import signal
import wftest as wt
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def run(self, *args, **kwargs):
        # Make sure WL-1 is enabled when starting wayfire
        shutil.copyfile('enabled.ini', 'wayfire.ini')
        return super().run(*args, **kwargs)

    def _run(self):
        _, pid = self.run_get_id('gtk_color_switcher cs')
        self.run_get_id('gtk_color_switcher cs')

        shutil.copyfile('disabled.ini', 'wayfire.ini')
        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGKILL)

        self.wait_ms(200) # crossfade animation
        if len(self._get_views()) != 1:
            return wt.Status.WRONG, 'Demo app crashed after disabling WL-1: ' + str(self._get_views())

        return wt.Status.OK, None
