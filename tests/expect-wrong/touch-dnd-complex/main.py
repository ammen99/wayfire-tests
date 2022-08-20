#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil
import time

def is_gui() -> bool:
    return True

# This test opens a special gtk client twice (gtk1 and gtk2), and x11_click_to_close in addition.
# The windows are then arranged next to each other.
# The special gtk client reports DnD action status to a file given on the command line.
#
# We need to verify that:
# 1) drag from gtk1 and drop on xterm does not do anything (but grab is released)
# 2) drag from gtk2 to gtk1 closes gtk1
# 3) drag from gtk2 to itself closes gtk2
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_drag_and_drop'):
            return wt.Status.SKIPPED, "Missing gtk_drag_and_drop (Did you compile test clients?)"
        if not shutil.which('x11_click_to_close'):
            return wt.Status.SKIPPED, "Missing x11_click_to_close"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _click_and_drag(self, src, dst):
        sx, sy = src
        tx, ty = dst

        NUM_ITERATIONS = 50

        # Focus the gtk client to workaround it starting with the wrong serial -
        # if we directly start dragging, GTK will start the drag with the serial
        # from wl_keyboard.enter
        self.socket.set_touch(0, sx, sy)
        self.socket.release_touch(0)

        for i in range(0, NUM_ITERATIONS):
            # Interpolate between src and dst
            progress = i / NUM_ITERATIONS
            cx = (1 - progress) * sx + progress * tx
            cy = (1 - progress) * sy + progress * ty
            self.socket.set_touch(0, cx, cy)
            time.sleep(0.001) # 1000Hz movement

        self.socket.set_touch(0, tx, ty)
        self.socket.release_touch(0)

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'WAYLAND_DEBUG=1 gtk_drag_and_drop', 'gtk1', '&> /tmp/log1')
        gtk2 = wu.LoggedProcess(self.socket, 'WAYLAND_DEBUG=1 gtk_drag_and_drop', 'gtk2', '&> /tmp/log2')
        self.socket.run('x11_click_to_close x11 100 0 100 100')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1', 'gtk2', 'x11']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        layout['x11'] = (200, 0, 100, 100)
        layout['gtk2'] = (400, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self._click_and_drag((50, 50), (150, 50))
        self.wait_for_clients(2)
        if not gtk1.expect_line("drag-begin"):
            return wt.Status.WRONG, 'gtk1 did not start drag: ' + gtk1.last_line
        if not gtk1.expect_line("drag-end"):
            return wt.Status.WRONG, 'gtk1 did not end drag: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has extra output: ' + gtk1.last_line

        self._click_and_drag((450, 50), (50, 50))
        self.wait_for_clients(2)
        if not gtk2.expect_line("drag-begin"):
            return wt.Status.WRONG, 'gtk2 did not start drag: ' + gtk2.last_line
        if not gtk2.expect_line("drag-end"):
            return wt.Status.WRONG, 'gtk2 did not end drag: ' + gtk2.last_line
        if not gtk1.expect_line("drag-drop"):
            return wt.Status.WRONG, 'gtk1 did not receive drag drop: ' + gtk1.last_line
        if not gtk1.expect_none() or not gtk2.expect_none():
            return wt.Status.WRONG, 'gtk1/gtk2 have extra output: ' + gtk1.last_line + '$' + gtk2.last_line

        if self._get_views() != ['gtk1', 'gtk2', 'x11']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
