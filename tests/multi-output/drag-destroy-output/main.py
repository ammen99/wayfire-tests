#!/bin/env python3

from wfipclib import check_geometry
import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.create_wayland_output()
        self.socket.run('gtk_color_switcher gcs')
        self.wait_for_clients_to_open(nr_clients=1)

        layout = {}
        layout['gcs'] = (0, 0, 200, 200, 'WL-1')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.click_and_drag('BTN_LEFT', 50, 50, 1250, 250, release=False)
        self.wait_for_clients(2)
        self.socket.destroy_wayland_output('WL-3')

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)

        info = self.socket.get_view_info_title('gcs')
        if not check_geometry(200, 200, 200, 200, info['geometry']):
            return wt.Status.WRONG, 'Wrong geometry: ' + str(info['geometry'])

        self.click_and_drag('BTN_LEFT', 210, 210, 250, 0, release=False)
        self.socket.destroy_wayland_output('WL-2')
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)

        info = self.socket.get_view_info_title('gcs')
        if not check_geometry(0, 0, 500, 500, info['geometry']):
            return wt.Status.WRONG, 'Wrong geometry: ' + str(info['geometry'])

        return wt.Status.OK, None
