#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# Check that we can move views to an empty wset without attached output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.run('gtk_color_switcher')
        self.wait_for_clients(2)

        self.socket.press_key('KEY_2')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_B')
        self.wait_for_clients(2)
        if not wi.check_geometry(0, 0, 500, 500, self.socket.get_view_info('gtk_color_switcher')['geometry']):
            return wt.Status.WRONG, 'The size of gtk-color-switcher has not been updated after selecting the wset!'

        # All is OK if wayfire has survied
        return wt.Status.OK, None
