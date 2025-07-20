#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Start scale, check that keyboard keys actually work
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal', 'gtk_color_switcher'])

    def _check_focus(self, terminal_focused: bool, msg: str):
        gcs = self.socket.get_view_info_title('gcs')['activated']
        terminal = self.socket.get_view_info(self.WESTON_TERMINAL_APP_ID)['activated']

        if terminal != terminal_focused:
            return f'weston-terminal has wrong activated state {terminal} {msg}'

        if gcs == terminal:
            return f'GCS has wrong activated state {gcs} {msg}'

        return None

    def _run(self):
        self.socket.run('weston-terminal --shell=/bin/sh')
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=2)

        # weston-terminal on the left, gcs on the right
        layout = {}
        layout[self.WESTON_TERMINAL_APP_ID] = (0, 0, 500, 500)
        layout['gcs'] = (500, 0, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # click weston-terminal
        self.socket.move_cursor(250, 250)
        self.socket.click_button('BTN_LEFT', 'full')

        # start scale, switch to gcs, exit
        self.socket.press_key('KEY_S')
        if err := self._check_focus(terminal_focused=True, msg='before KEY_RIGHT!'):
            return wt.Status.WRONG, err

        self.socket.press_key('KEY_RIGHT')
        if err := self._check_focus(terminal_focused=False, msg='after KEY_RIGHT!'):
            return wt.Status.WRONG, err

        self.socket.press_key('KEY_S')
        if err := self._check_focus(terminal_focused=False, msg='after scale!'):
            return wt.Status.WRONG, err

        if self.socket.ipc_rules_get_focused()['info']['app-id'] != 'gtk_color_switcher':
            return wt.Status.WRONG, 'Focused view is wrong at the end!'

        return wt.Status.OK, None
