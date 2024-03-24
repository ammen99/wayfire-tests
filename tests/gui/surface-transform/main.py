#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-transformed'])

    def _run(self):
        self.socket.run('weston-transformed')
        self.wait_for_clients_to_open(nr_clients=1)
        self.screenshot_prefix = "transform"

        for i in range(4):
            if err := self.take_screenshot(str(i)):
                return wt.Status.CRASHED, err
            self.socket.press_key('KEY_RIGHT')
            self.wait_for_clients(5)

        for i in range(3):
            a = self.screenshots[i]
            b = self.screenshots[i+1]
            code = wu.compare_images(a, b, a + '.delta.png', sensitivity=20)
            if code == wu.ImageDiff.SIZE_MISMATCH:
                return wt.Status.GUI_WRONG, 'Screenshot sizes are different: ' + a + ' vs. ' + b
            elif code == wu.ImageDiff.DIFFERENT:
                return wt.Status.GUI_WRONG, 'Screenshots are different: ' + a + ' vs. ' + b



        return wt.Status.OK, None
