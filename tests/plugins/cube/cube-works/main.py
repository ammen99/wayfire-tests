#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-background'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('wf-background')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_ms(1500) # for background fade-in

        layout = {}
        layout['nil'] = (0, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(4)

        self.socket.move_cursor(0, 0)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients()

        if error := self.take_screenshot('1-start-cube'):
            return wt.Status.CRASHED, error

        self.socket.move_cursor(100, 100)
        self.wait_for_clients()
        if error := self.take_screenshot('2-cube-rotated'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()
        if error := self.take_screenshot('3-cube-exited'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
