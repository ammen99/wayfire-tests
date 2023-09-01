#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['xterm'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('xterm -maximized')
        self.wait_for_clients(4)
        if self._get_views() != ['XTerm']:
            return wt.Status.WRONG, 'xterm did not open: ' + str(self._get_views())

        info = self.socket.get_view_info('XTerm')
        if not wi.check_geometry(0, 0, 1000, 500, info['geometry']):
            return wt.Status.WRONG, 'Terminators wm geometry is not maximized: ' + str(info['geometry'])

        if not wi.check_geometry(10, 20, 980, 470, info['base-geometry']):
            return wt.Status.WRONG, 'Terminators base geometry is not correct: ' + str(info['base-geometry'])

        return wt.Status.OK, None
