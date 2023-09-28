#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# Wayfire #1892: start two gtk_color_switchers, move one of them to the other output => there should be only one active view
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher'])

    def _run(self):
        # Create WL-2, ensure focus on WL-1
        self.socket.create_wayland_output()
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')

        self.socket.run('gtk_color_switcher gcs1')
        self.socket.run('gtk_color_switcher gcs2')
        self.wait_for_clients_to_open(nr_clients=2)

        layout = {}
        layout['gcs1'] = (0, 0, 100, 100)
        layout['gcs2'] = (200, 200, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Move gcs1 to WL-2
        self.socket.move_cursor(50, 50)
        self.click_and_drag('BTN_RIGHT', 50, 50, 700, 200)
        self.wait_for_clients()

        gcs1 = self.socket.get_view_info_title('gcs1')
        gcs2 = self.socket.get_view_info_title('gcs2')

        if not gcs1['state']['activated']:
            return wt.Status.WRONG, 'GCS1 is not active!'

        if gcs2['state']['activated']:
            return wt.Status.WRONG, 'GCS2 is active!'

        return wt.Status.OK, None
