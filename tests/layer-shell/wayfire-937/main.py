#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['layer_shell_delay_exclusive'])

    def _run(self):
        id, _ = self.run_get_id('layer_shell_delay_exclusive')

        # Wait for delay
        self.wait_ms(500)

        info = self.socket.get_view_info_id(id)
        assert info
        if info['bbox']['y'] + info['bbox']['height'] != 500:
            return wt.Status.WRONG, 'Wrong geometry at the end: ' + str(info['bbox'])

        return wt.Status.OK, None
