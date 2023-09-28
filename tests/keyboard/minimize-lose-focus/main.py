#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

# This test start a client and minimizes it. This should cause it to lose focus and become inactive.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_logger'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        # Start keylogger
        x11 = wu.LoggedProcess(self.socket, 'x11_logger', 'x11', '&> /tmp/log')
        self.wait_for_clients_to_open(nr_clients=1)

        x11.reset_logs()
        self.socket.press_key('KEY_M')
        self.wait_for_clients(2)

        try:
            x11.expect_line_throw('focus-out', 'after minimization')
        except Exception as e:
            return wt.Status.WRONG, str(e)

        state = self.socket.get_view_info_title('x11')
        if state['state']['activated']:
            return wt.Status.WRONG, 'View is still activated after minimization!'

        return wt.Status.OK, None
