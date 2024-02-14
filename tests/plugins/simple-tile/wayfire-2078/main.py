#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# Open a window, tile it, make it a dialog and change its size.
# We need to make sure that simple-tile completely dissociates from that window as it becomes a dialog.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def _run(self):
        self.socket.run('gtk_logger a /tmp/a tmpcli dialog-shortcut delay-dialog')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.press_key('KEY_O')
        self.wait_for_clients_to_open(nr_clients=2)

        # 100ms delay for the dialog set
        self.wait_ms(150)

        logger_g = self.socket.get_view_info_title('a')['geometry']
        if not wi.check_geometry(0, 0, 1000, 500, logger_g):
            return wt.Status.WRONG, 'Dialog is still tiled? ' + str(logger_g)

        return wt.Status.OK, None
