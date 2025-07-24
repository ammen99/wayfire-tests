#!/bin/env python3

import wftest as wt
import signal
def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wleird-layer-shell'])

    def check_state(self, id, state):
        info = self.socket.get_view_info_id(id)
        if info['activated'] != state:
            return f'view id={id} title={info["title"]} state is {info["activated"]}, expected {state}'
        return None

    def _run(self):
        id, _ = self.run_get_id('weston-terminal --shell=/bin/sh')
        if err := self.check_state(id, True):
            return wt.Status.WRONG, err

        def run_iteration(keep_activated: bool):
            self.socket.sock.set_option_values({'workarounds/keep_last_toplevel_activated' : keep_activated})

            _, pid_shell = self.run_get_id('wleird-layer-shell -l top -k exclusive')
            if err := self.check_state(id, keep_activated):
                return wt.Status.WRONG, f'keep={keep_activated} shell open: {err}'

            self.send_signal(pid_shell, signal.SIGKILL)
            self.wait_for_clients(2)

            if err := self.check_state(id, True):
                return wt.Status.WRONG, f'keep={keep_activated} shell closed: {err}'

            return wt.Status.OK, None

        status, msg = run_iteration(True)
        if status != wt.Status.OK:
            return status, msg

        status, msg = run_iteration(False)
        if status != wt.Status.OK:
            return status, msg

        return wt.Status.OK, None
