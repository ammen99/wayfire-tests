#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return True

# This tests opens two nested popups and clicks on the parent menu.
# The goal is to ensure that the menus stay ordered as they ought to.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_nested_popup'])

    def _get_views(self):
        return sorted([v['app-id'] for v in self.socket.list_views()])

    def _run(self):
        id, _ = self.run_get_id('gtk_nested_popup')

        main_info = self.socket.get_view_info_id(id)
        self.socket.move_cursor(main_info['geometry']['x'] + 20, main_info['geometry']['y'] + 20)
        self.socket.click_button('BTN_RIGHT', 'full')
        self.wait_for_clients_to_open(nr_clients=2)
        menu_id = [x for x in self.socket.list_views() if x['id'] != id][0]['id']

        menu_info = self.socket.get_view_info_id(menu_id)
        self.socket.move_cursor(menu_info['geometry']['x'] + 20, menu_info['geometry']['y'] + 20)
        self.wait_for_clients_to_open(nr_clients=3)
        nested_menu_id = [x for x in self.socket.list_views() if x['id'] != id and x['id'] != menu_id][0]['id']

        self.socket.click_button('BTN_LEFT', 'press')
        self.wait_for_clients()

        if err := self.take_screenshot('1-nested-open'):
            return wt.Status.WRONG, err

        self.socket.click_button('BTN_LEFT', 'release')
        nested_menu_info = self.socket.get_view_info_id(nested_menu_id)
        self.socket.move_cursor(nested_menu_info['geometry']['x'] + 20, nested_menu_info['geometry']['y'] + 20)
        self.socket.click_button('BTN_LEFT', 'full')
        self.wait_for_clients()

        if err := self.take_screenshot('2-nested-closed'):
            return wt.Status.WRONG, err

        return wt.Status.OK, None
