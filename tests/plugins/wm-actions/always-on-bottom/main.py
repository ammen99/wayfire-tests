#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This test opens overlapping clients and verifies that always-on-bottom views
# are below normal workspace views. It also checks mutual exclusion with
# always-on-top through IPC state reporting.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['x11_click_to_close'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _get_view(self, app_id):
        view = self.socket.get_view_info(app_id, mapped_only=True)
        if view is None:
            raise wt.TestEncounteredError('Missing view: ' + app_id)

        return view

    def _set_always_on_bottom(self, app_id, state):
        self.socket.send_json({
            'method': 'wm-actions/set-always-on-bottom',
            'data': {
                'view-id': self._get_view(app_id)['id'],
                'state': state,
            },
        })

    def _set_always_on_top(self, app_id, state):
        self.socket.send_json({
            'method': 'wm-actions/set-always-on-top',
            'data': {
                'view-id': self._get_view(app_id)['id'],
                'state': state,
            },
        })

    def _check_state(self, app_id, top, bottom):
        view = self._get_view(app_id)
        if view['always-on-top'] != top:
            return wt.Status.WRONG, 'Wrong always-on-top state: ' + str(view)

        if view['always-on-bottom'] != bottom:
            return wt.Status.WRONG, 'Wrong always-on-bottom state: ' + str(view)

        return wt.Status.OK, None

    def _run(self):
        self.socket.run('x11_click_to_close 1 0 0 100 100')
        self.wait_for_clients_to_open(nr_clients=1)
        self.socket.run('x11_click_to_close 2 0 0 100 100')
        self.wait_for_clients_to_open(nr_clients=2)

        self._set_always_on_top('2', True)
        self._set_always_on_bottom('2', True)
        status, msg = self._check_state('2', False, True)
        if status != wt.Status.OK:
            return status, msg

        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()
        if self._get_views() != ['2']:
            return wt.Status.WRONG, 'Always-on-bottom view received input: ' + str(self._get_views())

        self._set_always_on_top('2', True)
        status, msg = self._check_state('2', True, False)
        if status != wt.Status.OK:
            return status, msg

        self.socket.run('x11_click_to_close 3 0 0 100 100')
        self.wait_for_clients_to_open(nr_clients=2)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients()
        if self._get_views() != ['3']:
            return wt.Status.WRONG, 'Always-on-top view did not receive input: ' + str(self._get_views())

        return wt.Status.OK, None
