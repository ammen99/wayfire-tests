import lycon
import numpy as np
from enum import Enum
import wfipclib as wi
import traceback
import psutil
import time
import os
from pathlib import Path
from uuid import uuid4

class ImageDiff(Enum):
    SAME = 0
    DIFFERENT = 1
    SIZE_MISMATCH = 2

    def __eq__(self, other):
        return self.value == other.value

def compare_images(path1: str, path2: str, diff_log: str, sensitivity: float) -> ImageDiff:
    img1 = lycon.load(path1)
    img2 = lycon.load(path2)

    if img1.shape != img2.shape:
        return ImageDiff.SIZE_MISMATCH

    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)

    diff = np.abs(img1 - img2) / 255
    total_diff = np.sqrt(np.sum(diff * diff))
    if total_diff > sensitivity:
        lycon.save(diff_log, diff * 255.0)
        return ImageDiff.DIFFERENT

    return ImageDiff.SAME

# Error message or None
def take_screenshot(socket: wi.WayfireIPCClient, path: str) -> str | None:
    try:
        # Start grim
        pid = socket.run("grim " + path)
        if not ("result", "ok") in pid.items():
            return "Failed to run grim command in core - " + pid["error"]

        # Now wait for grim to finish
        while psutil.pid_exists(pid["pid"]):
            time.sleep(0.1)
        return None
    except:
        return "Failed to wait for grim: " + traceback.format_exc()

class LoggedProcess:
    def __init__(self, socket: wi.WayfireIPCClient, cmd: str, app_id: str, add_arg: str = ""):
        dir = "/tmp/wst/" + str(uuid4()) + "/";
        Path(dir).mkdir(parents=True, exist_ok=True)
        self.pid = socket.run("{} {} {} {}".format(cmd, app_id, dir + app_id, add_arg))["pid"]
        self.logfile = open(dir + app_id, "a+")
        self.logfile = open(dir + app_id, "r")
        self.last_line = ""
        os.set_blocking(self.logfile.fileno(), False)

    def reset_logs(self):
        # Just read until EOF
        while self.logfile.readline():
            pass

    def _read_next(self):
        self.last_line = self.logfile.readline()
        if not self.last_line:
            self.last_line = "<empty>"
        else:
            self.last_line = self.last_line[:-1] # Remove trailing newline

    def expect_line(self, line: str):
        self._read_next()
        return line == self.last_line

    def expect_none(self):
        self._read_next()
        return self.last_line == "<empty>"
