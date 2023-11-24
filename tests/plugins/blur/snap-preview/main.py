#!/bin/env python3

import wftest as wt

# The test requires to compare two blur images.
# The blur effect is not very stable, so wide, but small
# changes are expected. Therefore, we need a higher sensitivity
# for this test.
def sensitivity():
    return 5.0

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-background'])

    def _run(self):
        self.socket.run('weston-terminal')
        self.socket.run('wf-background')
        self.wait_for_clients_to_open(nr_clients=2)
        self.wait_ms(1500) # Wait for wf-background to start and be initialized

        layout = {}
        layout['nil'] = (0, 0, 200, 200, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        if error := self.take_screenshot('scene-setup'):
            return wt.Status.CRASHED, error

        self.socket.move_cursor(5, 5)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(500, 250) # Snap to the right half, wait for a preview
        self.wait_ms(300) # The preview indication is hardcoded for 200ms

        if error := self.take_screenshot('preview-blurred'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_ms(300) # The preview indication is hardcoded for 200ms

        if error := self.take_screenshot('terminal-snapped'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
