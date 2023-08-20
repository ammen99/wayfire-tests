#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_map_unmap'])

    def _run(self):
        self.socket.run('x11_map_unmap -a x11 -x 52 -y 52 -w 400 -h 400 -d 33 -r 3 &> /tmp/log')
        self.wait_ms(400)

        x11 = self.socket.get_view_info('x11')
        if not x11:
            return wt.Status.WRONG, 'x11_map_unmap not open?'

        if not wi.check_geometry(42, 42, 420, 420, x11['geometry']):
            return wt.Status.WRONG, "x11_map_unmap has wrong geometry {}!".format(x11['geometry'])
        return wt.Status.OK, None
