#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['wleird-shortcuts-inhibit'])

    def _run(self):
        pid = self.socket.run('wleird-shortcuts-inhibit')['pid']
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout['wleird-shortcuts-inhibit'] = (0, 0, 250, 500)
        layout['gcs'] = (250, 0, 250, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Make sure shortcuts-inhibit is active
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        if error := self.take_screenshot('1-start'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if error := self.take_screenshot('2-still-inhibited'):
            return wt.Status.CRASHED, error

        # Activate gcs, disable inhibitor
        self.socket.move_cursor(400, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if error := self.take_screenshot('3-no-inhibitor'):
            return wt.Status.CRASHED, error

        # Close expo
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)

        # Focus & activate inhibitor
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)
        if error := self.take_screenshot('4-inhibit-again'):
            return wt.Status.CRASHED, error

        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)

        # Deactivate inhibitor from the client
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if error := self.take_screenshot('5-expo-again'):
            return wt.Status.CRASHED, error

        # Reactivate inhibitor from the client
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients(2)
        self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(2)
        self.socket.ping()

        return wt.Status.OK, None
