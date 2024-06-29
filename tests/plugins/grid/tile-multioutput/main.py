#!/bin/env python3

import wftest as wt

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

        self.click_and_drag('BTN_LEFT', 900, 400, 501, 0)
        self.wait_for_clients(200)

        print(self.socket.list_views())
        maximized_g = self.socket.get_view_info('gcs')["geometry"]
        print(maximized_g)

        return wt.Status.OK, None
