#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients(2)

        self.socket.move_cursor(10, 10)

        # Show and hide repeatedly, odd number => must be hidden in the end
        for _ in range(9):
            self.socket.click_button('BTN_LEFT', 'full')
            self.wait_ms(50) # Make sure to toggle in the middle of the animation which is 200ms

        # Wait for animation to settle down
        self.wait_ms(300)
        if error := self.take_screenshot('minimized-hidden'):
            return wt.Status.CRASHED, error

        # Show and hide repeatedly, odd number => must be show in the end, as it was hidden before
        for _ in range(9):
            self.socket.click_button('BTN_LEFT', 'full')
            self.wait_ms(50) # Make sure to toggle in the middle of the animation which is 200ms

        self.wait_ms(300)
        if error := self.take_screenshot('minimized-restored'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
