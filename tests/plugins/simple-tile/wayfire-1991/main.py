#!/bin/env python3

import wftest as wt
import wfipclib as wi
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def run(self, *args, **kwargs):
        shutil.copyfile('scale-1x.ini', 'wayfire.ini')
        return super().run(*args, **kwargs)

    def _run(self):
        self.socket.press_key('KEY_A') # go to workspace on the bottom right
        self.wait_for_clients()
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=1)

        shutil.copyfile('scale-2x.ini', 'wayfire.ini')
        self.wait_for_clients(2)

        info = self.socket.get_view_info_title('gcs')
        if not wi.check_geometry(0, 0, 250, 250, info['bbox']):
            return wt.Status.WRONG, 'View has wrong geometry: ' + str(info['bbox'])

        return wt.Status.OK, None
