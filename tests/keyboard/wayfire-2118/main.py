#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return False

# Wayfire #2118
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _get_focused(self):
        focused = self.socket.ipc_rules_get_focused()['info']
        return focused['app-id'] if focused else 'None'

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (100, 100, 900, 900)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        focus = self._get_focused()
        if focus != self.WESTON_TERMINAL_APP_ID:
            return wt.Status.WRONG, f'weston-terminal should be focused in the beginning, instead focus is {focus}'

        self.socket.press_key('KEY_A')
        self.wait_for_clients(2)

        focus = self._get_focused()
        if focus != 'panel' and focus != '': # '' is in wf-panel gtk4, where the popup gets focus
            return wt.Status.WRONG, f'wf-panel menu did not get focus, instead focus is {focus}'

        self.socket.press_key('KEY_A')
        self.wait_for_clients(2)

        focus = self._get_focused()
        if focus != self.WESTON_TERMINAL_APP_ID:
            return wt.Status.WRONG, f'weston-terminal did not regain focus, instead focus is {focus}'

        return wt.Status.OK, None
