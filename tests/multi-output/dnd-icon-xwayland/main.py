#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This test opens a special gtk client twice on different outputs so that they overlap.
# Then, it proceeds to check that despite the overlap, the correct view is focused every time,
# i.e. it checks that a view's input region is confined to its output.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_drag_and_drop'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('GDK_BACKEND=x11 gtk_drag_and_drop gtk1 /tmp/a')
        self.socket.create_wayland_output()
        self.wait_for_clients(2)

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 200, 200, 'WL-1') # Overlaps the left half of WL-2
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Start a drag and move the drag icon to between the outputs
        self.socket.move_cursor(100, 100)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(150, 150)
        self.socket.move_cursor(170, 170)
        self.socket.move_cursor(350, 50)
        self.socket.move_cursor(350, 150)
        self.wait_for_clients(2)

        if error := self.take_screenshot('dnd-icon-active'):
            return wt.Status.CRASHED, error

        # Cancel DnD
        self.socket.click_button('BTN_LEFT', 'release')
        self.socket.move_cursor(355, 150)
        self.wait_for_clients()

        # Unfortunately, we can't take a screenshot because of animation, so we just
        # wait to make sure Wayfire doesn't crash
        return wt.Status.OK, None
