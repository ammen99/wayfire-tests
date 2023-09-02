#!/bin/env python3

import importlib
import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This test opens gedit and a gtk keyboard logger client side by side.
# Then, it opens a menu in gedit (xdg-popup) which should be automatically closed when clicking on the gtk logger client.
class WTest(wt.WayfireTest):
    def prepare(self):
        spec = importlib.util.find_spec('PyQt5.QtWidgets') # type: ignore
        if spec:
            return wt.Status.OK, None
        else:
            return wt.Status.SKIPPED, 'PyQt5.QtWidgets missing'

    def _run(self):
        self.socket.run('python3 client.py')
        self.wait_for_clients_to_open(nr_clients=1)

        maximized = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(0, 0, 1000, 500, maximized):
            return wt.Status.WRONG, 'Window is not maximized properly: ' + str(maximized)

        self.socket.press_key('KEY_M')
        self.wait_ms(200)

        restored = self.socket.get_view_info_title('test')['geometry']
        if not wi.check_geometry(0, 0, 300, 200, restored):
            return wt.Status.WRONG, 'Window is not restored properly: ' + str(maximized)

        return wt.Status.OK, None
