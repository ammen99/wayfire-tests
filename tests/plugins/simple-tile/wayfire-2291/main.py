#!/bin/env python3

import signal
from wfipclib import get_msg_template
import wftest as wt

def is_gui() -> bool:
    return False

# Start simple-tile on WL-1, ipc to toggle scale on WL-2 while drag is active: wayfire #2291
# Start scale, press one of the windows, kill it, and move: wayfire #2286, #2289, #2292, #2293
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _run(self):
        id, pid = self.run_get_id('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.create_wayland_output()

        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.run('gtk_color_switcher')
        self.wait_for_clients_to_open(nr_clients=2)

        self.click_and_drag('BTN_LEFT', 250, 250, 995, 300, release=False)
        self.wait_for_clients(2)

        output = [o['id'] for o in self.socket.list_outputs() if o['name'] == 'WL-2'][0]
        msg = get_msg_template('scale/toggle')
        msg['data']['output_id'] = output
        self.socket.send_json(msg)

        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'release')

        info = self.socket.get_view_info_id(id)
        assert info

        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, 'Wrong output!'

        sx = info['bbox']['x'] + info['bbox']['width'] / 2 + 500
        sy = info['bbox']['y'] + info['bbox']['height'] / 2
        self.socket.move_cursor(sx, sy)
        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)

        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients()

        return wt.Status.OK, None
