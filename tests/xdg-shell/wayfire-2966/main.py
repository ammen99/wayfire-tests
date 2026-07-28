#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

# This tests opens two nested popups by clicking once and moving through the menus.
# Release on the submenu should close the entire app (wayfire #2966)
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['gtk_nested_popup'])

    def _run(self):
        id, _ = self.run_get_id(
            'gtk_nested_popup --close-on-click --left-click')

        main_info = self.socket.get_view_info_id(id)
        self.socket.move_cursor(main_info['geometry']['x'] + 20, main_info['geometry']['y'] + 20)
        self.socket.click_button('BTN_LEFT', 'press')

        self.wait_for_clients_to_open(nr_clients=2)
        menu_id = [x for x in self.socket.list_views() if x['id'] != id][0]['id']

        menu_info = self.socket.get_view_info_id(menu_id)
        self.socket.move_cursor(menu_info['geometry']['x'] + 20, menu_info['geometry']['y'] + 20)
        self.wait_for_clients_to_open(nr_clients=3)
        nested_menu_id = [x for x in self.socket.list_views() if x['id'] != id and x['id'] != menu_id][0]['id']
        nested_menu_info = self.socket.get_view_info_id(nested_menu_id)
        self.socket.move_cursor(nested_menu_info['geometry']['x'] + 20, nested_menu_info['geometry']['y'] + 20)
        self.wait_ms(100)
        self.socket.move_cursor(nested_menu_info['geometry']['x'] + 21, nested_menu_info['geometry']['y'] + 21)
        self.wait_ms(20)
        self.socket.move_cursor(nested_menu_info['geometry']['x'] + 22, nested_menu_info['geometry']['y'] + 22)
        self.wait_ms(20)
        self.socket.move_cursor(nested_menu_info['geometry']['x'] + 23, nested_menu_info['geometry']['y'] + 23)
        self.wait_ms(20)

        self.socket.click_button('BTN_LEFT', 'release')
        self.wait_for_clients(2)

        if self.socket.list_views():
            return wt.Status.WRONG, 'Client did not close on release!'

        return wt.Status.OK, None
