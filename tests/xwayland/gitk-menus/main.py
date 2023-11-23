#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gitk'])

    def _run(self):
        self.socket.run('gitk')
        self.wait_for_clients(2)

        layout = {}
        layout['Gitk'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        if not self.socket.get_view_info('Gitk'):
            return wt.Status.WRONG, 'Gitk not running?'

        # Move around a bit, see that wayfire doesn't crash
        self.socket.move_cursor(10, 10)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        v = self.socket.get_view_info_title("#bar#file")
        if v and v['state'] and 'focusable' in v['state'] and v['state']['focusable']:
            return wt.Status.WRONG, "Wrong focusable state for gitk menu, should be false! (Wayfire #2007)"

        for i in range(1, 10):
            self.socket.move_cursor(i * 10, 10)
            self.wait_for_clients()
        for i in range(10, 0, -1):
            self.socket.move_cursor(i * 10, 10)
            self.wait_for_clients()

        self.wait_for_clients(2)
        if not self.socket.get_view_info('Gitk'):
            return wt.Status.WRONG, 'Gitk not running?'

        if err := self.take_screenshot('final'):
            return wt.Status.CRASHED, err

        return wt.Status.OK, None
