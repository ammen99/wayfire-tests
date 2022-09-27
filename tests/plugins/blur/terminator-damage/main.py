#!/bin/env python3

import wftest as wt

# The test requires to compare two blur images.
# The blur effect is not very stable, so wide, but small
# changes are expected. Therefore, we need a higher sensitivity
# for this test.
def sensitivity():
    return 200.0

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
        self.socket.run('terminator')
        self.socket.run('wf-background')
        for _ in range(10):
            # Wait a loong time for wf-background to start
            if len(self._get_views()) != 2:
                self.wait_for_clients()

        layout = {}
        layout['terminator'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(5, 5)
        self.socket.click_button('BTN_LEFT', 'press')

        self._move_to(5, 5, 500, 500, 3)
        self._move_to(500, 500, 0, 0, 10)
        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
