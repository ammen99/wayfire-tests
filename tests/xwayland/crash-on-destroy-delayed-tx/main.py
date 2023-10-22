#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return False

# Open a Xwayland client, move it with a delayed transaction and kill the client in the meantime
# Open x11_map_unmap on the non-focused output => it should be reconfigured on the current output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_click_to_close'])

    def _run(self):
        # Make sure x11_click_to_close does not get focus initially, but only after moving
        self.socket.move_cursor(250, 250)

        pid = self.socket.run('x11_click_to_close x11 0 0 200 200')['pid']
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['x11'] = (100, 100, 200, 200)
        self.socket.delay_next_tx()
        self.socket.layout_views(layout)

        self.send_signal(pid, signal.SIGKILL)
        self.wait_ms(300) # wait for tx timeout

        if self.socket.list_views():
            return wt.Status.WRONG, "Clients are still open?"

        return wt.Status.OK, None
