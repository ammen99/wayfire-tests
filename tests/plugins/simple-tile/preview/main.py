#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_for_clients(2)

        self.socket.move_cursor(150, 150)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(255, 255)
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more

        if error := self.take_screenshot('preview-shown'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
