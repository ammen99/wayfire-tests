#!/bin/env python3

import wftest as wt
import wfutil as wu
import signal

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['fcitx5', 'gtk_logger'])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard text-input')
        self.wait_for_clients_to_open(nr_clients=1)
        pid = self.socket.run('WAYLAND_DEBUG=1 dbus-launch --exit-with-session ../fcitx-wrapper/start-fcitx5.sh &> /tmp/flog')['pid']
        self.wait_for_clients(5) # wait for im+handshake

        try:
            gtk1.expect_line_throw('keyboard-enter')
            self.socket.set_key_state('KEY_F', True)
            self.wait_for_clients(2)
            self.send_signal(pid, signal.SIGKILL)
            self.wait_for_clients(2)

            #gtk1.expect_line_throw('key-release 33')
            #gtk1.expect_none_throw()
        except wu.WrongLogLine as e:
            return wt.Status.WRONG, e.args[0]

        clients = self.socket.list_views()
        if len(clients) != 2:
            return wt.Status.WRONG, f'Wrong number of clients {clients}'

        return wt.Status.OK, None
