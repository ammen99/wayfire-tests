#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# This test opens gedit and a gtk keyboard logger client side by side.
# Then, it opens a menu in gedit (xdg-popup) which should be automatically closed when clicking on the gtk logger client.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['terminator'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('terminator -M')
        self.wait_for_clients(2)
        if self._get_views() != ['terminator']:
            return wt.Status.WRONG, 'Terminator did not open: ' + str(self._get_views())

        info = self.socket.get_view_info('terminator')
        if not wi.check_geometry(0, 0, 1000, 500, info['geometry']):
            return wt.Status.WRONG, 'Terminators wm geometry is not maximized: ' + str(info['geometry'])

        if not wi.check_geometry(10, 20, 980, 470, info['base-geometry']):
            return wt.Status.WRONG, 'Terminators base geometry is not correct: ' + str(info['base-geometry'])

        return wt.Status.OK, None
