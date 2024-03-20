#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# Simple test which starts weston-terminal maximized, then closes it by clicking on the close button

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def check(self, ids, sizes, outputs):
        for idx, vid in enumerate(ids):
            v = self.socket.get_view_info_id(vid)
            if not v:
                return f"View vid={vid} not found"

            if sizes[idx] != (v['geometry']['x'], v['geometry']['y'], v['geometry']['width'], v['geometry']['height']):
                return f"View vid={vid} has wrong size: {v['geometry']['x']}, {v['geometry']['y']} {v['geometry']['width']}x{v['geometry']['height']}, should be {sizes[idx]}"

            if outputs[idx] != v['output-name']:
                return f"View vid={vid} has wrong output: {v['output-name']}, should be {outputs[idx]}"

        return None


    def _run(self):
        # Tile wt1, wt2 on WL-1, wt3 on WL-2
        gcs1_id, _ = self.run_get_id('gtk_color_switcher')
        gcs2_id, _ = self.run_get_id('gtk_color_switcher')
        self.socket.create_wayland_output()

        self.socket.move_cursor(750, 250) # Focus WL-2
        self.socket.click_button('BTN_LEFT', 'full')
        gcs3_id, _ = self.run_get_id('gtk_color_switcher')
        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(0, 0, 245, 500), (255, 0, 245, 500), (0, 0, 500, 500)], ['WL-1', 'WL-1', 'WL-2']):
            return wt.Status.WRONG, err + " initially."

        # Click on titlebar, exit immediately
        self.socket.move_cursor(750, 5) # Focus WL-2
        self.socket.click_button('BTN_LEFT', 'full')

        # Self-drop
        self.click_and_drag('BTN_LEFT', 750, 5, 750, 250)
        self.wait_for_clients()

        # Start dragging from WL-1:
        self.socket.move_cursor(150, 150)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(255, 255)
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more

        if error := self.take_screenshot('1-preview-shown'):
            return wt.Status.CRASHED, error

        self.socket.move_cursor(750, 5)
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more

        if error := self.take_screenshot('2-preview-shown'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more

        if error := self.take_screenshot('3-dropped'):
            return wt.Status.CRASHED, error

        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(0, 0, 500, 245), (0, 0, 500, 500), (0, 255, 500, 245)], ['WL-2', 'WL-1', 'WL-2']):
            return wt.Status.WRONG, err + " after drag to WL-2."

        # Swap two tiled views between different outputs
        self.click_and_drag('BTN_LEFT', 750, 400, 250, 250)

        self.wait_for_clients()
        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(0, 0, 500, 245), (0, 255, 500, 245), (0, 0, 500, 500)], ['WL-2', 'WL-2', 'WL-1']):
            return wt.Status.WRONG, err + " after swap between WL-1 and WL-2."

        # Start scale on WL-2
        self.socket.move_cursor(750, 250)
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.press_key('KEY_S')
        self.wait_for_clients()

        info = self.socket.get_view_info_id(gcs1_id)
        assert info
        sx = info['bbox']['x'] + info['bbox']['width'] / 2 + 500
        sy = info['bbox']['y'] + info['bbox']['height'] / 2

        self.click_and_drag('BTN_LEFT', sx, sy, 250, 495, release=False)
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more

        if error := self.take_screenshot('4-preview-after-scale'):
            return wt.Status.CRASHED, error

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_ms(300) # Preview is hardcoded for 200ms, wait a bit more
        if error := self.take_screenshot('5-tiled-after-scale'):
            return wt.Status.CRASHED, error

        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(0, 255, 500, 245), (0, 0, 500, 500), (0, 0, 500, 245)], ['WL-1', 'WL-2', 'WL-1']):
            return wt.Status.WRONG, err + " after drag from scale to WL-1."

        self.click_and_drag('BTN_LEFT', 250, 150, 750, 5)
        self.wait_for_clients()

        if error := self.take_screenshot('6-drag-to-scale'):
            return wt.Status.CRASHED, error

        if err := self.check([gcs1_id, gcs2_id, gcs3_id], [(0, 0, 500, 500), (0, 255, 500, 245), (0, 0, 500, 245)], ['WL-1', 'WL-2', 'WL-2']):
            return wt.Status.WRONG, err + " after drag from WL-1 to scale."

        return wt.Status.OK, None
