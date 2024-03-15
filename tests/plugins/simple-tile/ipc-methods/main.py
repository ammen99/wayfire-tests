#!/bin/env python3

import wftest as wt
import wfipclib as wi
import wfutil as wu
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

    def _get_new_view_id(self, ids):
        all_ids = [v['id'] for v in self.socket.list_views() if v['mapped']]
        for id in all_ids:
            if id not in ids:
                ids += [id]
                return id
        return None

    def _find_by_id(self, id):
        for v in self.socket.list_views():
            if v['id'] == id:
                return v
        raise Exception("View with id {} not found".format(id))

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
        ids = []
        layout = self._tiling_layout(1, 0, 0)
        if layout != {}:
            return wt.Status.WRONG, "Tiling layout should be empty: {}".format(layout)

        pid = self.socket.run('gtk_color_switcher')['pid']
        self.wait_for_clients_to_open(nr_clients=1)
        self.send_signal(pid, signal.SIGUSR1)
        gcs_id = self._get_new_view_id(ids)

        layout = self._tiling_layout(1, 0, 0)
        expected_layout = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'view-id': gcs_id}
        if layout != expected_layout:
            return wt.Status.WRONG, "Tiling layout should contain just one view: {}".format(layout)

        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=2)
        wt1_id = self._get_new_view_id(ids)

        self.socket.run('weston-terminal')
        self.wait_for_clients_to_open(nr_clients=3)
        wt2_id = self._get_new_view_id(ids)

        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', '') # not tiled
        self.wait_for_clients_to_open(nr_clients=4)
        logger1_id = self._get_new_view_id(ids)

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
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk2', '')
        self.wait_for_clients_to_open(nr_clients=5)
        logger2_id = self._get_new_view_id(ids)

        layout = self._tiling_layout(2, 0, 0)
        expected_layout = {'geometry': {'height': 500, 'width': 500, 'x': 0, 'y': 0}, 'percent': 1.0, 'view-id': logger2_id}
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
                    {'weight': 1, 'view-id': wt1_id}, # weston-terminal #1
                    ]
        }

        self.socket.send_json(msg)
        self.wait_for_clients(2)
        self.socket.press_key('KEY_A')
        self.socket.press_key('KEY_2') # Focus workspace with all the tiled views
        self.wait_for_clients()

        layout = self._tiling_layout_raw(2, 0, 0)
        if 'error' not in layout:
            return wt.Status.WRONG, "Tiling layout on 2,0,0 should be empty: {}".format(layout)

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
            return wt.Status.WRONG, "Tiling layout on 1,1,0 should contain just weston-terminal: {}".format(layout)

        self.wait_for_clients(4)

        for id in [gcs_id, logger1_id, logger2_id, wt1_id]:
            info = self._find_by_id(id)['bbox']
            geometry = self._find_geometry_in_layout_by_id(id, expected_layout)
            assert geometry
            if info['x'] != geometry['x'] or info['y'] != geometry['y'] or info['width'] != geometry['width'] or info['height'] != geometry['height']:
                return wt.Status.WRONG, "View with id {} has wrong geometry: {} after retiling, expected {}".format(id, info, geometry)

        layout = self._tiling_layout(1, 0, 0) # Check first workspace, we should have just weston-terminal #2 now
        if layout != {'geometry': {'height': 500, 'width': 500, 'x': -500, 'y': 0}, 'percent': 1.0, 'view-id': wt2_id}:
            return wt.Status.WRONG, "Tiling layout on 1,0,0 should contain just weston-terminal: {}".format(layout)

        if err := self.take_screenshot('final-tiling'):
            return wt.Status.CRASHED, err

        # Untile weston-terminal on ws 1, 0, 0
        msg = wi.get_msg_template("simple-tile/set-layout")
        msg['data']['wset-index'] = 1
        msg['data']['workspace'] = {}
        msg['data']['workspace']['x'] = 0
        msg['data']['workspace']['y'] = 0
        msg['data']['layout'] = {'vertical-split': []}
        print(self.socket.send_json(msg))
        self.wait_for_clients(2)
        layout = self._tiling_layout(1, 0, 0) # Check first workspace, we should have just weston-terminal now
        if layout != {}:
            return wt.Status.WRONG, "Tiling layout on 1,0,0 should be empty at the end: {}".format(layout)

        return wt.Status.OK, None
