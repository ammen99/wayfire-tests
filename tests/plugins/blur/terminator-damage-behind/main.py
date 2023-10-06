#!/bin/env python3

import wftest as wt
import signal

def is_gui() -> bool:
    return True

# This client tiles weston-terminal two times and opens a view on top.
# Then it proceeds to check that the whole sublayer is moved to the top
# when clicking on the tiled views.
class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['terminator', 'gtk_color_switcher'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        gcs_pid = self.socket.run('gtk_color_switcher gcs')['pid']
        self.wait_for_clients(2)

        layout = {}
        layout['gcs'] = (250, 250, 500, 500)
        self.socket.layout_views(layout)
        self.wait_for_clients(2)

        self.socket.run('terminator -m')
        self.socket.run('terminator -m')
        self.wait_for_clients(4) # Terminator startup may be slow

        if error := self.take_screenshot('scene-setup'):
            return wt.Status.CRASHED, error

        # Damage behind terminator and see that blur expands damage
        self.send_signal(gcs_pid, signal.SIGUSR1)
        self.wait_for_clients(2)

        if error := self.take_screenshot('final'):
            return wt.Status.CRASHED, error
        return wt.Status.OK, None
