#!/bin/env python3

import wftest as wt
import wfipclib as wi

def is_gui() -> bool:
    return False

# Wayfire #1695
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        self.socket.create_wayland_output()
        self.socket.move_cursor(250, 250) # Focus WL-1
        self.socket.click_button('BTN_LEFT', 'full')
        self.socket.run('weston-terminal --shell=/bin/sh -m')
        self.wait_for_clients_to_open(nr_clients=1)

        self.click_and_drag('BTN_RIGHT', 50, 50, 750, 0) # Maximize on WL-2
        self.wait_for_clients(2)

        info = self.socket.get_view_info('nil')
        if not wi.check_geometry(0, 0, 500, 500, info['geometry']):
            return wt.Status.WRONG, f'weston-terminal has invalid geometry after dragging with binding: {str(info["geometry"])}'
        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, f'weston-terminal is on the wrong output after dragging with binding: {info["output"]}'

        # Drag via titlebar this time, back to the first output, but less than snap-off threshold
        sx = 510
        sy = 10
        self.click_and_drag('BTN_LEFT', sx, sy, 250, 0)
        self.wait_for_clients(2)

        info = self.socket.get_view_info('nil')
        if not wi.check_geometry(0, 0, 500, 500, info['geometry']):
            return wt.Status.WRONG, f'Try 1: weston-terminal has invalid geometry after dragging by titlebar: {str(info["geometry"])}'
        if info['output-name'] != 'WL-2':
            return wt.Status.WRONG, f'Try 1: weston-terminal is on the wrong output after dragging by titlebar: {info["output"]}'

        # Drag via titlebar this time, back to the first output, this time exceed the snap-off threshold
        # First wait a bit so that weston-terminal doesn't register a double click
        self.wait_ms(100)
        sx = 700
        sy = 10
        self.click_and_drag('BTN_LEFT', sx, sy, 250, 0)
        self.wait_for_clients(2)

        info = self.socket.get_view_info('nil')
        if not wi.check_geometry(0, 0, 500, 500, info['geometry']):
            return wt.Status.WRONG, f'Try 2: weston-terminal has invalid geometry after dragging by titlebar: {str(info["geometry"])}'
        if info['output-name'] != 'WL-1':
            return wt.Status.WRONG, f'Try 2: weston-terminal is on the wrong output after dragging by titlebar: {info["output"]}'

        return wt.Status.OK, None
