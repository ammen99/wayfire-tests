#!/bin/env python3

import wftest as wt
def is_gui() -> bool:
    return False

# This test checks that wf-shell's popups work correctly and receive correct focus
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'wf-panel'])

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('wf-panel -c wf-shell.ini')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (100, 100, 900, 900)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.move_cursor(25, 25) # On the menu
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_T') # Should start filtering in the menu

        focused = self.socket.ipc_rules_get_focused()['info']
        if focused['title'] != 'layer-shell' and focused['title'] != '': # '' in wf-panel gtk4, popup has no title
            return wt.Status.WRONG, f'wf-panel did not get input, instead is {focused['title']}!'

        self.wait_for_clients(2)

        self.socket.move_cursor(800, 800) # On weston-terminal
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients(2)
        self.socket.press_key('KEY_T') # Goes to weston-terminal
        self.wait_for_clients(2)

        focused = self.socket.ipc_rules_get_focused()['info']
        if focused['app-id'] != self.WESTON_TERMINAL_APP_ID:
            return wt.Status.WRONG, 'wf-panel did not let go of input!'

        return wt.Status.OK, None
