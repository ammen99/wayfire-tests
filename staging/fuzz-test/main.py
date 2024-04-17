#!/bin/env python3

import wftest as wt
from time import sleep
import os
import signal
import traceback
import subprocess


def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def run(self, wayfire_path: str, log: str):
        try:
            self.run_wayfire(wayfire_path, log)
            self.socket.create_wayland_output()
            self.socket.run("kitty --hold -- sh fuzz.sh")
            timeout = 15
            sleep(timeout)

            assert self._wayfire_process
            os.killpg(self._wayfire_gid, signal.SIGINT)
            if status := self._wayfire_process.wait(5.0):
                return wt.Status.CRASHED, "Wayfire process exited with status {}".format(status)

        except subprocess.TimeoutExpired:
            assert self._wayfire_process
            print("Wayfire did not terminate after SIGINT! Process PID is {}, killing after 1 minute".format(self._wayfire_process.pid))
            sleep(60.0)
            return wt.Status.CRASHED, "Wayfire did not terminate!"

        except Exception as _:
            return wt.Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()

        return wt.Status.OK, None
