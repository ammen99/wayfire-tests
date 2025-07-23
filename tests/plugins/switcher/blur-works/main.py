#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['terminator', 'wf-background'])

    def _move_to(self, sx, sy, x, y, steps):
        for i in range(steps+1):
            self.socket.move_cursor(sx + i / steps * (x - sx), sy + i / steps * (y - sy))
            self.wait_for_clients()

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('terminator -e /bin/sh')
        self.socket.run('wf-background')
        self.wait_ms(1500)

        layout = {}
        layout['terminator'] = (0, 0, 1000, 1000)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.press_key('KEY_N')
        if error := self.take_screenshot('switcher-active'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
