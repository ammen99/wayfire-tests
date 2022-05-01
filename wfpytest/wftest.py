from enum import Enum
from typing import Tuple, Optional
from wfipclib import WayfireIPCClient
import subprocess
import os
import time

class Status(Enum):
    OK = ("OK", "green")
    WRONG = ("WRONG", "red")
    CRASHED = ("CRASHED", "red")
    SKIPPED = ("SKIPPED", "yellow")

    def __eq__(self, other):
        return self.value == other.value

class WayfireTest:
    def __init__(self):
        self._wayfire_process = None
        self.socket: WayfireIPCClient = None #type:ignore
        self._socket_name = "/tmp/wt.socket"

    def prepare(self):
        pass

    def run(self, wayfire_path: str, _: str) -> Tuple[Status, Optional[str]]:
        return Status.SKIPPED, "Test for \"" + wayfire_path + "\" not implemented?"

    def run_wayfire(self, wayfire_path: str, logfile: str):
        # Run wayfire with specified socket name for IPC communication
        env = os.environ.copy()
        env['_WAYFIRE_SOCKET'] = self._socket_name

        with open(logfile, "w+") as log:
            self._wayfire_process = subprocess.Popen([wayfire_path, '-c', self.locate_cfgfile()], env=env, stdout=log, stderr=log)
            time.sleep(1) # Leave a bit of time for Wayfire to initialize
            self.socket = WayfireIPCClient(self._socket_name)

    def locate_cfgfile(self) -> str:
        # This works, because the test runner switches into the tests' directory
        return 'wayfire.ini'

    def cleanup(self):
        if self._wayfire_process:
            self._wayfire_process.kill()

