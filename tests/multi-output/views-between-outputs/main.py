#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens a special gtk client twice on different outputs so that they overlap.
# Then, it proceeds to check that despite the overlap, the correct view is focused every time,
# i.e. it checks that a view's input region is confined to its output.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_logger', 'wleird-gamma-blend'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.move_cursor(0, 0)
        self.socket.run('gtk_logger gtk1 /tmp/a')
        self.socket.run('gtk_logger gtk2 /tmp/b')
        self.socket.run('wleird-gamma-blend')
        self.socket.create_wayland_output()
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2', 'nil']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (250, 0, 500, 500, 'WL-1') # Overlaps the left half of WL-2
        layout['gtk2'] = (500, 0, 500, 500, 'WL-1') # Overlaps WL-2, but not visible on WL-1 because on workspace on the right
        layout['nil'] = (-100, -100, 400, 400, 'WL-2')
        self.socket.layout_views(layout)
        self.wait_for_clients(2)
        if error := self.take_screenshot('scene-setup'):
            return wt.Status.CRASHED, error

        # Make sure WL-1 is focused
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.press_key('KEY_E')
        self.wait_for_clients()
        if error := self.take_screenshot('with-expo'):
            return wt.Status.CRASHED, error

        return wt.Status.OK, None
