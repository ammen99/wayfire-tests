#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['firefox'])

    def _run(self):
        self.socket.run('firefox')
        self.wait_ms(1000)

        layout = {}
        layout['firefox'] = (0, 0, 1000, 1000)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(980, 120)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_ms(500)

        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
