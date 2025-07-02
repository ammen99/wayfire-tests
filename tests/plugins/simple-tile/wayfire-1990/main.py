#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# Open a Xwayland dialog and make sure it isn't tiled automatically
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['eog'])

    def _run(self):
        self.socket.run('GDK_BACKEND=x11 eog')
        self.wait_for_clients_to_open(nr_clients=1)
        self.wait_ms(100) # Wait for things to settle down
        gedit_id = self.socket.get_view_info('Eog', mapped_only=True)['id']

        self.socket.set_key_state('KEY_LEFTCTRL', True)
        self.socket.set_key_state('KEY_O', True)
        self.socket.set_key_state('KEY_O', False)
        self.socket.set_key_state('KEY_LEFTCTRL', False)
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_for_clients(4)

        gedit_geometry = [v for v in self.socket.list_views() if v['id'] == gedit_id][0]['geometry']
        if not wi.check_geometry(0, 0, 1000, 500, gedit_geometry):
            return wt.Status.WRONG, 'Gedit geometry is not correct with dialog: ' + str(gedit_geometry)

        return wt.Status.OK, None
