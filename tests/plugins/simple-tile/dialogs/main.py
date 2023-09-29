#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_special'])

    def _run(self):
        self.socket.run('gtk_special a')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_O')
        self.wait_for_clients_to_open(nr_clients=2)

        if not wi.check_geometry(0, 0, 500, 500, self.socket.get_view_info_title('a')['geometry']):
            return wt.Status.WRONG, 'Dialogs are maybe also tiled2?'

        return wt.Status.OK, None
