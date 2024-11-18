#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['gcs'] = (0, 0, 500, 500, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.click_and_drag_steps('BTN_LEFT', [(900, 400), (0, 0), (501, 1)])
        self.wait_for_clients(4)

        info = self.socket.get_view_info_title('gcs')
        if not wi.check_geometry(0, 0, 250, 250, info['geometry']):
            return wt.Status.WRONG, "wrong maximized geometry: " + str(info['geometry'])
        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, "wrong output name: " + info['output-name']

        self.click_and_drag_steps('BTN_LEFT', [(600, 100), (0, 0), (502, 250), (995, 495)])
        self.wait_for_clients(4)

        info = self.socket.get_view_info_title('gcs')
        if not wi.check_geometry(250, 250, 250, 250, info['geometry']):
            return wt.Status.WRONG, "wrong maximized geometry after second move: " + str(info['geometry'])
        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, "wrong output name: " + info['output-name']


        return wt.Status.OK, None
