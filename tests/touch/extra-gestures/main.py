
#!/bin/env python3

import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'touch')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo app did not open: ' + str(self._get_views())

        # position the view
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients()

        # Try tap-to-close with 2 fingers
        self.socket.set_touch(0, 50, 50)
        self.socket.set_touch(0, 55, 51) # Slight movement
        self.socket.set_touch(1, 70, 70)
        self.socket.release_touch(1)
        self.socket.release_touch(0)

        # => wayfire, => close(client) => unmap(wayfire)
        self.wait_for_clients(3)
        if self._get_views() != []:
            return wt.Status.WRONG, 'App was not closed? ' + str(self._get_views())

        return wt.Status.OK, None

