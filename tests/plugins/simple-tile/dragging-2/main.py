#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def check(self, ids, sizes):
        for idx, vid in enumerate(ids):
            v = self.socket.get_view_info_id(vid)
            if not v:
                return f"View vid={vid} not found"

            if sizes[idx] != (v['geometry']['x'], v['geometry']['y'], v['geometry']['width'], v['geometry']['height']):
                return f"View vid={vid} has wrong size: {v['geometry']['x']}, {v['geometry']['y']} {v['geometry']['width']}x{v['geometry']['height']}, should be {sizes[idx]}"

        return None

    def drag_window_to(self, winid, tx, ty, release=True):
        info = self.socket.get_view_info_id(winid);
        assert info
        sx = info['bbox']['x'] + info['bbox']['width'] / 2
        sy = info['bbox']['y'] + info['bbox']['height'] / 2
        self.click_and_drag('BTN_LEFT', sx, sy, tx, ty, release)

    def _run(self):
        gcs1_id, _ = self.run_get_id('gtk_color_switcher')
        gcs2_id, _ = self.run_get_id('gtk_color_switcher')
        if err := self.check([gcs1_id, gcs2_id], [(0, 0, 245, 500), (255, 0, 245, 500)]):
            return wt.Status.WRONG, err + " initially."

        self.drag_window_to(gcs1_id, 450, 250, release=False)
        self.wait_ms(400) # for simple-tile preview animation
        gcs3_id, _ = self.run_get_id('gtk_color_switcher')
        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)

        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(171, 0, 157, 500), (0, 0, 161, 500), (338, 0, 162, 500)]):
            return wt.Status.WRONG, err + " after unsuccessful drag."

        self.drag_window_to(gcs1_id, 450, 250, release=True)
        self.wait_for_clients(2)
        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(338, 0, 162, 500), (0, 0, 161, 500), (171, 0, 157, 500)]):
            return wt.Status.WRONG, err + " after successful drag."

        return wt.Status.OK, None
