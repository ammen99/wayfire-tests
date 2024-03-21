#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return True

# Check that we can move views to an empty wset without attached output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _tiling_layout_raw(self, wset, x, y):
        msg = wi.get_msg_template("simple-tile/get-layout")
        msg['data']['wset-index'] = wset
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = x
        msg['data']['workspace']['y'] = y
        return self.socket.send_json(msg)

    def _tiling_layout(self, wset, x, y):
        return self._tiling_layout_raw(wset, x, y)['layout']

    def _run(self):
        id, _ = self.run_get_id('weston-terminal')

        EMPTY_LAYOUT = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'vertical-split': []}
        EMPTY_LAYOUT_DEFAULT_RES = {'geometry': {'height': 1080, 'width': 1920, 'x': 0, 'y': 0}, 'percent': 1.0, 'vertical-split': []}
        WITH_TERMINAL = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'vertical-split': [
            {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'view-id': id}]}

        layout = self._tiling_layout(1, 0, 0)
        if layout != WITH_TERMINAL:
            return wt.Status.WRONG, "Tiling layout should have just wt in the beginning: {}".format(layout)

        # Send wt to wset 2
        self.socket.press_key('KEY_2')
        layout = self._tiling_layout(1, 0, 0)
        if layout != EMPTY_LAYOUT:
            return wt.Status.WRONG, "Tiling layout should be empty after sending wt to wset 2: {}".format(layout)

        # Go to wset 2, untile wt, send to 1 => should not become tiled!
        self.socket.press_key('KEY_B')
        layout = self._tiling_layout(2, 0, 0)
        if layout != WITH_TERMINAL:
            return wt.Status.WRONG, "Tiling layout should have wt on wset 2: {}".format(layout)

        self.socket.press_key('KEY_T')
        self.socket.press_key('KEY_1')
        layout = self._tiling_layout(1, 0, 0)
        if layout != EMPTY_LAYOUT_DEFAULT_RES:
            return wt.Status.WRONG, "Tiling layout should be empty on wset 1 in the end: {}".format(layout)

        layout = self._tiling_layout(2, 0, 0)
        if layout != EMPTY_LAYOUT:
            return wt.Status.WRONG, "Tiling layout should be empty on wset 2 in the end: {}".format(layout)


        return wt.Status.OK, None
