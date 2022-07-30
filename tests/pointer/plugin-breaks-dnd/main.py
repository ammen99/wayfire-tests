
#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test open the DnD demo client, starts a DnD operation but breaks it by starting a plugin
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_drag_and_drop'):
            return wt.Status.SKIPPED, "Missing gtk_drag_and_drop (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_drag_and_drop', 'gtk1')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the view, go to gtk1 and start DnD
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.socket.move_cursor(50, 50)
        self.socket.click_button('BTN_LEFT', 'press')
        self.socket.move_cursor(55, 55)
        self.socket.move_cursor(75, 75)
        self.wait_for_clients(2)
        if not gtk1.expect_line("drag-begin"):
            return wt.Status.WRONG, 'gtk1 did not start DnD: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output: ' + gtk1.last_line

        # Start expo => DnD should be reset
        self.socket.press_key('KEY_E')
        self.wait_for_clients(2)
        if not gtk1.expect_line("drag-end"):
            return wt.Status.WRONG, 'gtk1 did not end drag: ' + gtk1.last_line
        if not gtk1.expect_none():
            return wt.Status.WRONG, 'gtk1 has trailing output2: ' + gtk1.last_line

        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        return wt.Status.OK, None
