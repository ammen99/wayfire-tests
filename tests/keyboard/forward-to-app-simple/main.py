#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return True

# This test opens the gtk special client and uses it to open dialogs and then close them with
# simple keypresses. It also clicks a few times to attempt changing the focus, which should fail,
# as dialogs are always focused and not the main view.
class WTest(wt.WayfireTest):
    def prepare(self):
        if not shutil.which('gtk_special'):
            return wt.Status.SKIPPED, "Missing gtk_special (Did you compile test clients?)"
        return wt.Status.OK, None

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('gtk_special a')
        self.wait_for_clients(2)
        if self._get_views() != ['a']:
            return wt.Status.WRONG, 'Demo did not open: ' + str(self._get_views())

        # Close dialog b
        self.socket.press_key('KEY_Q')
        self.wait_for_clients(3)
        if self._get_views() != []:
            return wt.Status.WRONG, 'Demo did not get keyboard input: ' + str(self._get_views())

        return wt.Status.OK, None
