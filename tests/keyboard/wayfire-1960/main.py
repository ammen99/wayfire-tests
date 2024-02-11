#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test opens a few gtk_special dialogs and verifies that focus is passed around correctly.
# The it opens 3 dialogs and orders them linearly on the screen, so that it can toggle focus and verify the activated states.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_special'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _hover(self, view_info):
        sx, sy = (view_info['geometry']['x'] + 10, view_info['geometry']['y'] + 10)
        self.socket.move_cursor(sx, sy)
        return sx, sy

    def _click(self, view_info):
        self._hover(view_info)
        self.socket.click_button('BTN_LEFT', 'full')

    def _check_active_states(self, states):
        views = self.socket.list_views()
        for v in views:
            title = v['title']
            if title in states and states[title] != v['activated']:
                return f"Wrong state of view {v['title']}: expected {states[title]}"

        return None

    def _run(self):
        self.socket.run('gtk_special a b c d')
        self.wait_for_clients_to_open(nr_clients=4)

        if self._get_views() != ['a', 'b', 'c', 'd']:
            return wt.Status.WRONG, 'Incorrect setup: ' + str(self._get_views())

        if err := self._check_active_states({'a': False, 'b': False, 'c': False, 'd': True}):
            return wt.Status.WRONG, f'Opened: {err}'

        sx, sy = self._hover(self.socket.get_view_info_title('d'))
        self.click_and_drag('BTN_LEFT', sx, sy, 900, 300, steps=20) # d is rightmost
        self.wait_for_clients()

        sx, sy = self._hover(self.socket.get_view_info_title('c'))
        self.click_and_drag('BTN_LEFT', sx, sy, 600, 300, steps=20)
        self.wait_for_clients()

        sx, sy = self._hover(self.socket.get_view_info_title('b'))
        self.click_and_drag('BTN_LEFT', sx, sy, 300, 300, steps=20)
        self.wait_for_clients()

        sx, sy = self._hover(self.socket.get_view_info_title('a'))
        self.click_and_drag('BTN_LEFT', sx, sy, 0, 300, steps=20) # a is leftmost
        self.wait_for_clients()

        self._click(self.socket.get_view_info_title('d'))
        if err := self._check_active_states({'a': False, 'b': False, 'c': False, 'd': True}):
            return wt.Status.WRONG, f'Click d: {err}'

        self._click(self.socket.get_view_info_title('a'))
        if err := self._check_active_states({'a': False, 'b': False, 'c': False, 'd': True}):
            return wt.Status.WRONG, f'Click a: {err}'

        self._click(self.socket.get_view_info_title('b'))
        if err := self._check_active_states({'a': False, 'b': True, 'c': False, 'd': False}):
            return wt.Status.WRONG, f'Click b: {err}'

        return wt.Status.OK, None
