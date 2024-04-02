#!/bin/env python3

import wftest as wt
import wfipclib as wi
import signal

def is_gui() -> bool:
    return False

# Check that we can move views to an empty wset without attached output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        wt_id, pid = self.run_get_id('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)

        self.socket.delay_next_tx()
        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)

        msg = wi.get_msg_template("simple-tile/set-layout")
        msg['data']['wset-index'] = 1
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = 1
        msg['data']['workspace']['y'] = 0
        msg['data']['layout'] = {'vertical-split': [{'view-id': wt_id, 'weight': 1}]}
        if 'error' not in self.socket.send_json(msg):
            return wt.Status.WRONG, 'simple-tile should not tile pending-unmapped views!'

        return wt.Status.OK, None
