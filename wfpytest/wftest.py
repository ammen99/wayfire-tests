from enum import Enum
from typing import Tuple, Optional, List, Any
from wfipclib import WayfireIPCClient, get_msg_template
from pathlib import Path
from uuid import uuid4
import wfutil as wu
from datetime import datetime

import subprocess
import signal
import psutil
import os
import time
import traceback
import shutil
import random

class Status(Enum):
    OK = ("OK", "green")
    WRONG = ("WRONG", "red")
    GUI_WRONG = ("GUI_WRONG", "red")
    CRASHED = ("CRASHED", "red")
    SKIPPED = ("SKIPPED", "yellow")

    def __eq__(self, other):
        return self.value == other.value

def get_now():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

class TestEncounteredError(Exception):
    pass

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

        Path("/tmp/wst/").mkdir(parents=True, exist_ok=True)
        id = str(uuid4())
        self._socket_name = "/tmp/wst/wayfire-" + id + ".socket"
        self._ipc_duration = 0.1
        self.screenshots = []
        self.screenshot_prefix = ""
        self.subtest_data: Any = None
        self.ev_socket: WayfireIPCClient | None = None

    def watch(self, events: List[str]) -> WayfireIPCClient:
        self.ev_socket = WayfireIPCClient(self._socket_name)
        sub_cmd = get_msg_template('window-rules/events/watch')
        sub_cmd['data']['events'] = events
        self.ev_socket.send_json(sub_cmd)
        return self.ev_socket

    def send_signal(self, parent_pid, sig=signal.SIGTERM):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            raise Exception("No such process!")

        children = parent.children(recursive=True)
        os.kill(parent_pid, sig)
        for process in children:
            os.kill(process.pid, sig)

    def wait_for_clients(self, times=1):
        time.sleep(self._ipc_duration * times) # Wait for clients to start/process events

    def _get_mapped_views(self):
        return [v for v in self.socket.list_views() if v['mapped']]

    def _get_new_view_id(self, ids):
        all_ids = [v['id'] for v in self.socket.list_views() if v['mapped']]
        for id in all_ids:
            if id not in ids:
                return id
        return None

    def run_get_id(self, cmd):
        ids = [v['id'] for v in self._get_mapped_views()]
        pid = self.socket.run(cmd)['pid']
        self.wait_for_clients_to_open(len(ids) + 1)
        return self._get_new_view_id(ids), pid

    def wait_for_clients_to_open(self, nr_clients: int, waits = 10, interval = 100, message: str | None = None):
        for _ in range(waits):
            if len(self._get_mapped_views()) != nr_clients:
                self.wait_ms(interval)

        if len(self._get_mapped_views()) != nr_clients:
            if message is None:
                raise TestEncounteredError("Clients did not open: {}".format(nr_clients))
            else:
                raise TestEncounteredError(message)

    def wait_ms(self, ms):
        time.sleep((self._ipc_duration / 0.1) * ms * 0.001)

    def require_test_clients(self, clients_list):
        for client in clients_list:
            if not shutil.which(client):
                return Status.SKIPPED, "Missing {} (Did you compile test clients?)".format(client)
        return Status.OK, None

    def take_screenshot(self, stage: str):
        full_path = self.screenshot_prefix + "-" + stage + ".png"
        self.screenshots.append(full_path)
        return wu.take_screenshot(self.socket, full_path)

    def prepare(self) -> Tuple[Status, Optional[str]]:
        return Status.OK, None

    def _run(self) -> Tuple[Status, Optional[str]]:
        return Status.SKIPPED, "Test for not implemented?"

    def get_subtests(self) -> List[Tuple[str, Any]]:
        return [('--default--', None)]

    # By default, a test starts Wayfire, executes self._run(), then checks that wayfire didn't crash
    # and exits successfully.
    # Thus, tests only need to implement _run() and don't need to duplicate the setup/teardown code
    def run_once(self, wayfire_path: str, log: str) -> Tuple[Status, Optional[str]]:
        try:
            self.run_wayfire(wayfire_path, log)
            status, msg = self._run()
            if status != Status.OK:
                return status, msg

            if self.socket.ping():
                return Status.OK, None
            else:
                return Status.WRONG, "Wayfire failed to respond to ping"

        except TestEncounteredError as e:
            return Status.WRONG, str(e)
        except Exception as _:
            return Status.CRASHED, "Wayfire or client socket crashed, " + traceback.format_exc()

    def run(self, wayfire_path: str, log: str, configuration: str | None) -> Tuple[Status, Optional[str]]:
        needs_reset = False
        tests_run = 0

        for name, subtest in self.get_subtests():
            self.subtest_data = subtest

            if configuration is not None and name != configuration:
                continue

            if needs_reset:
                self.cleanup()

            status, msg = self.run_once(wayfire_path, log)
            if status != Status.OK:
                return status, str(msg) + ("" if (name == "--default--") else ("(configuration " + name + ")"))
            else:
                tests_run += 1
                needs_reset = True

        if tests_run > 1:
            return Status.OK, f'{tests_run} subtests'

        return Status.OK, None

    def click_and_drag(self, button, start_x, start_y, end_x, end_y, release=True, steps = 10):
        dx = end_x - start_x
        dy = end_y - start_y

        self.socket.move_cursor(start_x, start_y)
        self.socket.click_button(button, 'press')
        for i in range(steps+1):
            self.socket.move_cursor(start_x + dx * i // steps, start_y + dy * i // steps)
        if release:
            self.socket.click_button(button, 'release')

    def run_wayfire(self, wayfire_path: str, logfile: str):
        # Run wayfire with specified socket name for IPC communication
        env = os.environ.copy()
        env['_WAYFIRE_SOCKET'] = self._socket_name

        with open(logfile, "w") as log:
            log.write(f'Wayfire instance starting at {get_now()} with socket {self._socket_name}\n')
            log.flush()

            self._wayfire_process = subprocess.Popen([wayfire_path, '-c', self.locate_cfgfile()],
                    env=env, stdout=log, stderr=log, preexec_fn=os.setsid)
            self._wayfire_gid = os.getpgid(self._wayfire_process.pid)
            time.sleep(1.5 + random.uniform(0, 1)) # Leave a bit of time for Wayfire to initialize + add random offset to desync multiple tests in parallel

            log.write(f'Test code starting: {get_now()}\n')
            log.flush()
            self.socket = WayfireIPCClient(self._socket_name)

    def locate_cfgfile(self) -> str:
        # This works, because the test runner switches into the tests' directory
        return 'wayfire.ini'

    def cleanup(self):
        if self._wayfire_process:
            try:
                os.killpg(self._wayfire_gid, signal.SIGTERM)
                time.sleep(0.5)
                os.killpg(self._wayfire_gid, signal.SIGKILL)
            except:
                pass
