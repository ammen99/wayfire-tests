#!/bin/env python3

import wftest as wt
import wfipclib as wi
import signal

def is_gui() -> bool:
    return True

# Check that we can move views to an empty wset without attached output
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_color_switcher', 'weston-terminal', 'gtk_logger'])

    def _tiling_layout_raw(self, wset, x, y):
        msg = wi.get_msg_template("simple-tile/get-layout")
        msg['data']['wset-index'] = wset
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = x
        msg['data']['workspace']['y'] = y
        return self.socket.send_json(msg)

    def _tiling_layout(self, wset, x, y):
        return self._tiling_layout_raw(wset, x, y)['layout']

    def _find_geometry_in_layout_by_id(self, id, layout):
        if 'view-id' in layout:
            if layout['view-id'] == id:
                return layout['geometry']
            else:
                return None

        if 'horizontal-split' in layout:
            for child in layout['horizontal-split']:
                result = self._find_geometry_in_layout_by_id(id, child)
                if result is not None:
                    return result

        if 'vertical-split' in layout:
            for child in layout['vertical-split']:
                result = self._find_geometry_in_layout_by_id(id, child)
                if result is not None:
                    return result

        return None

    def _run(self):
        EMPTY_LAYOUT = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'vertical-split': []}
        EMPTY_LAYOUT_LEFT = {'geometry': {'height': 500, 'width': 500, 'x': -500, 'y': 0}, 'percent': 1.0, 'vertical-split': []}

        layout = self._tiling_layout(1, 0, 0)
        if layout != EMPTY_LAYOUT:
            return wt.Status.WRONG, "Tiling layout should be empty: {}".format(layout)

        pids = []
        gcs_id, pid = self.run_get_id('gtk_color_switcher')
        pids.append(pid)

        layout = self._tiling_layout(1, 0, 0)
        expected_layout = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0,
                           'vertical-split': [{'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'view-id': gcs_id}]}
        if layout != expected_layout:
            return wt.Status.WRONG, "Tiling layout should contain just one view: {}".format(layout)

        wt1_id, pid = self.run_get_id('weston-terminal')
        pids.append(pid)
        wt2_id, pid = self.run_get_id('weston-terminal')
        pids.append(pid)
        logger1_id, pid = self.run_get_id('gtk_logger gtk1 /dev/null')
        pids.append(pid)

        layout = self._tiling_layout(1, 0, 0)
        expected_layout = {
                'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0},
                'percent': 1.0,
                'vertical-split': [
                    {'geometry': {'height': 500, 'width': 166, 'x': 0, 'y': 0}, 'percent': 0.332, 'view-id': gcs_id},
                    {'geometry': {'height': 500, 'width': 167, 'x': 166, 'y': 0}, 'percent': 0.334, 'view-id': wt1_id},
                    {'geometry': {'height': 500, 'width': 167, 'x': 333, 'y': 0}, 'percent': 0.334, 'view-id': wt2_id},
                    ]}

        if layout != expected_layout:
            return wt.Status.WRONG, 'Tiling layout with three views at startup is wrong: {}'.format(layout)

        self.socket.press_key('KEY_B')

        logger2_id, pid = self.run_get_id('gtk_logger gtk2 /dev/null')
        pids.append(pid)

        layout = self._tiling_layout(2, 0, 0)
        expected_layout = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0,
                           'vertical-split': [{'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'view-id': logger2_id}]}
        if layout != expected_layout:
            return wt.Status.WRONG, "Tiling layout on wset 2 should contain just one view: {}".format(layout)

        # Set layout and make sure all views are transferred to correct workspaces and workspace sets
        msg = wi.get_msg_template("simple-tile/set-layout")
        msg['data']['wset-index'] = 1
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = 1
        msg['data']['workspace']['y'] = 0

        msg['data']['layout'] = {
                'horizontal-split': [
                    {'weight': 1.0, 'view-id': gcs_id},
                    {'weight': 1, 'vertical-split': [
                        {'weight': 250, 'view-id': logger1_id},
                        {'weight': 250, 'view-id': logger2_id},
                        ]},
                    ]
        }

        # Try incremental changes to the layout
        self.socket.send_json(msg)
        msg['data']['layout']['horizontal-split'].append({'weight': 1, 'view-id': wt1_id})
        self.socket.send_json(msg)
        self.wait_for_clients(2)
        self.socket.press_key('KEY_A')
        self.socket.press_key('KEY_2') # Focus workspace with all the tiled views
        self.wait_for_clients()

        layout = self._tiling_layout_raw(2, 0, 0)
        if 'error' not in layout:
            return wt.Status.WRONG, "Tiling layout on 2,0,0 should be empty: {}".format(layout)

        # Invalid layout: duplicate view id
        msg['data']['layout'] = {
                'horizontal-split': [
                    {'weight': 1.0, 'view-id': gcs_id},
                    {'weight': 1.0, 'view-id': gcs_id}
                    ]}
        if 'error' not in self.socket.send_json(msg):
            return wt.Status.WRONG, "Tiling layout with duplicate view ids should not be allowed!"

        layout = self._tiling_layout(1, 1, 0)
        expected_layout = {
                'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0},
                'horizontal-split': [
                    {'geometry': {'height': 166, 'width': 500, 'x': 0, 'y': 0}, 'percent': 0.332, 'view-id': gcs_id},
                    {'geometry': {'height': 166, 'width': 500, 'x': 0, 'y': 166}, 'percent': 0.332,
                     'vertical-split': [
                         {'geometry': {'height': 166, 'width': 250, 'x': 0, 'y': 166}, 'percent': 0.5, 'view-id': logger1_id},
                         {'geometry': {'height': 166, 'width': 250, 'x': 250, 'y': 166}, 'percent': 0.5, 'view-id': logger2_id}
                         ]},
                    {'geometry': {'height': 168, 'width': 500, 'x': 0, 'y': 332}, 'percent': 0.336, 'view-id': wt1_id}
                    ], 'percent': 1.0}

        if layout != expected_layout:
            return wt.Status.WRONG, "Tiling layout on 1,1,0 should contain all views: {}".format(layout)

        self.wait_for_clients(4)

        for id in [gcs_id, logger1_id, logger2_id, wt1_id]:
            info = self.socket.get_view_info_id(id)['bbox'] # type: ignore
            geometry = self._find_geometry_in_layout_by_id(id, expected_layout)
            assert geometry
            if info['x'] != geometry['x'] or info['y'] != geometry['y'] or info['width'] != geometry['width'] or info['height'] != geometry['height']:
                return wt.Status.WRONG, "View with id {} has wrong geometry: {} after retiling, expected {}".format(id, info, geometry)

        layout = self._tiling_layout(1, 0, 0) # Check first workspace, we should have just weston-terminal #2 now
        expected_layout = {'geometry': {'height': 500, 'width': 500, 'x': -500, 'y': 0}, 'percent': 1.0,
                           'vertical-split': [{'geometry': {'height': 500, 'width': 500, 'x': -500, 'y': 0}, 'percent': 1.0, 'view-id': wt2_id}]}
        if layout != expected_layout:
            return wt.Status.WRONG, "Tiling layout on 1,0,0 should contain just weston-terminal: {}".format(layout)

        if err := self.take_screenshot('final-tiling'):
            return wt.Status.CRASHED, err

        # Untile a few views
        msg = wi.get_msg_template("simple-tile/set-layout")
        msg['data']['wset-index'] = 1
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = 1
        msg['data']['workspace']['y'] = 0
        msg['data']['layout'] = {'vertical-split': []}
        print(self.socket.send_json(msg))

        # Untile weston-terminal on ws 1, 0, 0
        msg = wi.get_msg_template("simple-tile/set-layout")
        msg['data']['wset-index'] = 1
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = 0
        msg['data']['workspace']['y'] = 0
        msg['data']['layout'] = {'vertical-split': []}
        print(self.socket.send_json(msg))
        self.wait_for_clients(2)

        layout = self._tiling_layout(1, 1, 0)
        if layout != EMPTY_LAYOUT:
            return wt.Status.WRONG, "Tiling layout on 1,1,0 should be empty at the end: {}".format(layout)

        layout = self._tiling_layout(1, 0, 0)
        if layout != EMPTY_LAYOUT_LEFT:
            return wt.Status.WRONG, "Tiling layout on 1,0,0 should be empty at the end: {}".format(layout)

        for pid in pids:
            self.send_signal(pid, signal.SIGKILL)
        self.wait_for_clients(4)

        return wt.Status.OK, None
