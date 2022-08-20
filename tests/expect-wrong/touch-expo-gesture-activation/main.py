
#!/bin/env python3

import wfipclib as wi
import wfutil as wu
import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# Test that during pinch in 3, the fingers are released when expo is activated
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_logger'):
            return wt.Status.SKIPPED, "Missing gtk_logger (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gtk1 = wu.LoggedProcess(self.socket, 'gtk_logger', 'gtk1', 'touch')
        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Demo apps did not open: ' + str(self._get_views())

        # position the views
        layout = {}
        layout['gtk1'] = (0, 0, 100, 100)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        # Put down the 3 fingers for pinch in
        self.socket.set_touch(0, 10, 10)
        self.socket.set_touch(1, 90, 15)
        self.socket.set_touch(2, 46, 87)

        # Pinch-in
        self.socket.set_touch(0, 45, 35)
        self.socket.set_touch(1, 50, 33)
        self.socket.set_touch(2, 49, 40)

        self.wait_for_clients(2)
        if self._get_views() != ['gtk1']:
            return wt.Status.WRONG, 'Apps crashed? ' + str(self._get_views())

        # Select workspace to verify expo has received the touch
        for i in range(3):
            self.socket.release_touch(i)

        self.socket.set_touch(0, 450, 450) # Workspace 2,2
        self.socket.release_touch(0)
        self.wait_for_clients() # Wait for expo to close itself

        view = self.socket.get_view_info_title('gtk1')
        if not wi.check_geometry(-500, -500, 100, 100, view['geometry']):
            return wt.Status.WRONG, 'Expo did not switch to workspace? ' + str(view)

        return wt.Status.OK, None
