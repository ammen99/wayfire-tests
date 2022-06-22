from enum import Enum
from typing import Tuple, Optional
from wfipclib import WayfireIPCClient
import subprocess
import signal
import os
import time
import traceback

class Status(Enum):
    OK = ("OK", "green")
    WRONG = ("WRONG", "red")
    CRASHED = ("CRASHED", "red")
    SKIPPED = ("SKIPPED", "yellow")

    def __eq__(self, other):
        return self.value == other.value

class WayfireTest:
    # An approximation of how long clients take to start and communicate with Wayfire
    # If your PC is slow, this duration can be increased, making every test wait longer
    # for clients.
    # In the end, this also results in longer testing times, but what can we do ...
    def _set_ipc_duration(self, duration):
        self._ipc_duration = duration

    def __init__(self):
        self._wayfire_process = None
        self.socket: WayfireIPCClient = None #type:ignore
        self._socket_name = "/tmp/wt.socket"
        self._ipc_duration = 0.1

    def wait_for_clients(self, times=1):
        time.sleep(self._ipc_duration * times) # Wait for clients to start/process events

    def prepare(self) -> Tuple[Status, Optional[str]]:
        return Status.OK, None

    def _run(self) -> Tuple[Status, Optional[str]]:
        return Status.SKIPPED, "Test for not implemented?"

    # By default, a test starts Wayfire, executes self._run(), then checks that wayfire didn't crash
    # and exits successfully.
    # Thus, tests only need to implement _run() and don't need to duplicate the setup/teardown code
    def run(self, wayfire_path: str, log: str) -> Tuple[Status, Optional[str]]:
        try:
            self.run_wayfire(wayfire_path, log)
            status, msg = self._run()
            if status != Status.OK:
                return status, msg

            if self.socket.ping():
                return Status.OK, None
            else:
                return Status.WRONG, "Wayfire failed to respond to ping"

        except Exception as _:
            return Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()

    def run_wayfire(self, wayfire_path: str, logfile: str):
        # Run wayfire with specified socket name for IPC communication
        env = os.environ.copy()
        env['_WAYFIRE_SOCKET'] = self._socket_name

        with open(logfile, "w") as log:
            self._wayfire_process = subprocess.Popen([wayfire_path, '-c', self.locate_cfgfile()],
                    env=env, stdout=log, stderr=log, preexec_fn=os.setsid)
            time.sleep(0.5) # Leave a bit of time for Wayfire to initialize
            self.socket = WayfireIPCClient(self._socket_name)

    def locate_cfgfile(self) -> str:
        # This works, because the test runner switches into the tests' directory
        return 'wayfire.ini'

    def cleanup(self):
        if self._wayfire_process:
            pgrp = os.getpgid(self._wayfire_process.pid)
            os.killpg(pgrp, signal.SIGKILL)
