#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Check that drag and drop between scale instances on different outputs works fine
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        # Open 2x weston-terminal on WL-1, start scale
        self.socket.run('weston-terminal')
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=2)
        self.socket.press_key('KEY_S')

        # Create/focus WL-2 and open 2x weston-terminal there as well, start scale.
        self.socket.create_wayland_output()
        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.run('weston-terminal')
        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=4)
        self.socket.press_key('KEY_S')
        self.wait_for_clients()

        # Drag one weston-terminal from WL-2 to WL-1
        wt_wl2 = [v for v in self.socket.list_views() if v['output-name'] == 'WL-2'][0]
        x = 500 + wt_wl2['bbox']['x'] + wt_wl2['bbox']['width'] / 2
        y = wt_wl2['bbox']['y'] + wt_wl2['bbox']['height'] / 2
        self.click_and_drag('BTN_LEFT', x, y, 250, 0)
        self.wait_for_clients()

        # Drag one weston-terminal from WL-2 to WL-1
        wt_wl1 = [v for v in self.socket.list_views() if v['id'] == wt_wl2['id']][0]
        if wt_wl1['output-name'] != 'WL-1':
            return wt.Status.WRONG, 'Wrong output, not WL-1'
        if (wt_wl1['base-geometry']['width'] <= wt_wl1['bbox']['width'] or
            wt_wl1['base-geometry']['height'] <= wt_wl1['bbox']['height']):
            return wt.Status.WRONG, 'weston-terminal is not scaled on WL-1!'

        x = wt_wl1['bbox']['x'] + wt_wl1['bbox']['width'] / 2
        y = wt_wl1['bbox']['y'] + wt_wl1['bbox']['height'] / 2
        self.click_and_drag('BTN_LEFT', x, y, 750, 0)
        self.wait_for_clients()

        wt_wl2_2 = [v for v in self.socket.list_views() if v['id'] == wt_wl2['id']][0]
        if wt_wl2_2['output-name'] != 'WL-2':
            return wt.Status.WRONG, 'Wrong output, not WL-2'

        self.wait_for_clients(2)
        return wt.Status.OK, None
