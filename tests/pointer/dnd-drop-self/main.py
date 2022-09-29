#!/bin/env python3

import wfutil as wu
import wftest as wt
import time

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_drag_and_drop'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _click_and_drag(self, src, dst):
        sx, sy = src
        tx, ty = dst

        NUM_ITERATIONS = 50
        self.socket.move_cursor(sx, sy)
        # Focus the gtk client to workaround it starting with the wrong serial -
        # if we directly start dragging, GTK will start the drag with the serial
        # from wl_keyboard.enter
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.click_button('BTN_LEFT', 'release')
        self.socket.click_button('BTN_LEFT', 'press')

        for i in range(0, NUM_ITERATIONS):
            # Interpolate between src and dst
            progress = i / NUM_ITERATIONS
            cx = (1 - progress) * sx + progress * tx
            cy = (1 - progress) * sy + progress * ty
            self.socket.move_cursor(cx, cy)
            time.sleep(0.001) # 1000Hz movement

        self.socket.move_cursor(tx, ty)
        self.socket.click_button('BTN_LEFT', 'release')

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_drag_and_drop', 'gtk1')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self._click_and_drag((10, 10), (90, 90))
        self.wait_for_clients(2)
        if not gtk1.expect_line("drag-begin"):
            return wt.Status.WRONG, 'gtk1 did not start drag the first time: ' + gtk1.last_line
        if not gtk1.expect_line("drag-drop"):
            return wt.Status.WRONG, 'gtk1 did not drop the first time: ' + gtk1.last_line
        if not gtk1.expect_line("drag-end"):
            return wt.Status.WRONG, 'gtk1 did not end drag the first time: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has extra output after first drag: ' + gtk1.last_line

        self._click_and_drag((10, 10), (90, 90))
        self.wait_for_clients(2)
        if not gtk1.expect_line("drag-begin"):
            return wt.Status.WRONG, 'gtk1 did not start drag the second time: ' + gtk1.last_line
        if not gtk1.expect_line("drag-drop"):
            return wt.Status.WRONG, 'gtk1 did not drop the second time: ' + gtk1.last_line
        if not gtk1.expect_line("drag-end"):
            return wt.Status.WRONG, 'gtk1 did not end drag the second time: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has extra output after second drag: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
