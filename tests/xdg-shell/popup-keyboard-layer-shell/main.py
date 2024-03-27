#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['layer_shell_kb_popup'])

    def _run(self):
        id, _ = self.run_get_id('layer_shell_kb_popup')
        self.wait_for_clients_to_open(nr_clients=1)

        # right click in the middle to open context menu (xdg-popup)
        info = self.socket.get_view_info_id(id)
        assert info
        self.socket.move_cursor(info['geometry']['x'] + info['geometry']['width'] / 2,
                                info['geometry']['y'] + info['geometry']['height'] / 2)
        self.socket.click_button('BTN_RIGHT', 'full')
        if not self.wait_for_clients_to_open(nr_clients=2):
            return wt.Status.WRONG, 'Failed to open context menu'

        # Select second item in the menu, which closes.
        self.socket.press_key('KEY_DOWN')
        self.socket.press_key('KEY_DOWN')
        self.socket.press_key('KEY_ENTER')
        self.wait_ms(100)
        if len(self.socket.list_views()) != 0:
            return wt.Status.WRONG, 'App did not close'

        return wt.Status.OK, None
