#!/bin/env python3

import wftest as wt
import shutil

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['terminator'])

    def _get_views(self):
        return sorted([v['title'] for v in self.socket.list_views()])

    def _run(self):
        self.socket.run('terminator -e /bin/sh')
        self.wait_for_clients(4) # Terminator has a slow startup

        shutil.copyfile('wayfire-no-blur.ini', 'wayfire.ini')
        self.wait_for_clients()
        shutil.copyfile('wayfire-blur.ini', 'wayfire.ini')
        self.wait_for_clients()
        shutil.copyfile('wayfire-no-blur.ini', 'wayfire.ini')
        self.wait_for_clients()
        shutil.copyfile('wayfire-blur.ini', 'wayfire.ini')
        self.wait_for_clients()

        return wt.Status.OK, None
