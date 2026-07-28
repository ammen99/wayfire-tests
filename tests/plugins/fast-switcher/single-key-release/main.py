#!/bin/env python3

import wftest as wt
import wfutil as wu

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger'])

    def get_subtests(self):
        return [('fast-switcher', ('fast-switcher', 'KEY_F3')),
                ('switcher', ('switcher', 'KEY_F4'))]

    def _focused(self):
        return self.socket.ipc_rules_get_focused()['info']

    def _focused_is(self, title):
        focused = self._focused()
        return focused and focused['title'] == title

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'keyboard')
        gtk2 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', 'keyboard')
        self.wait_for_clients_to_open(nr_clients=2)

        self.socket.layout_views({
            'gtk1': (0, 0, 500, 500),
            'gtk2': (500, 0, 500, 500),
        })
        self.wait_for_clients(2)

        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)

        if not self._focused_is('gtk1'):
            return wt.Status.WRONG, f'gtk1 should be focused before fast-switcher activation: {self._focused()}'

        gtk1.reset_logs()
        gtk2.reset_logs()

        try:
            plugin_name, activate_key = self.subtest_data
            self.socket.press_key(activate_key)
            self.wait_for_clients(2)

            if not self._focused_is('gtk2'):
                return wt.Status.WRONG, f'gtk2 should be focused after {plugin_name} activation: {self._focused()}'

            gtk1.expect_line_throw('keyboard-leave', f'after {plugin_name} activation')
            gtk1.expect_none_throw(f'old focused client after {plugin_name} activation')
            gtk2.expect_line_throw('keyboard-enter', f'after {plugin_name} activation')
            gtk2.expect_none_throw(f'new focused client after {plugin_name} activation')

            self.socket.set_key_state('KEY_A', True)
            self.wait_for_clients(2)

            gtk1.expect_none_throw('old focused client after KEY_A')
            gtk2.expect_line_throw('key-press 30', 'new focused client after KEY_A')
            gtk2.expect_none_throw('new focused client after KEY_A')
            self.socket.set_key_state('KEY_A', False)
        except Exception as e:
            return wt.Status.WRONG, e.args[0]

        return wt.Status.OK, None
