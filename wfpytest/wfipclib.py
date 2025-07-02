from wayfire import WayfireSocket
from wayfire.extra.stipc import Stipc
from wayfire.core.template import get_msg_template
from typing import Any
import select


class WayfireIPCClient:
    def __init__(self, socket_name: str):
        self.sock = WayfireSocket(socket_name)
        self.stipc = Stipc(self.sock)

        self.original_read_msg = self.sock.read_message
        self.sock.read_message = self.wrap_read_message

    # pywayfire raises exceptions when wayfire reports an error, instead, we want to handle them in the tests.
    # so we wrap the read_message method.
    def wrap_read_message(self):
        try:
            return self.original_read_msg()
        except Exception as e:
            return {'error': str(e.args[0])}

    def read_message(self, timeout = None):
        if timeout is None:
            return self.wrap_read_message()

        readable, _, _ = select.select([self.sock.client], [], [], timeout)
        if readable:
            return self.wrap_read_message()
        else:
            return None

    def ping(self):
        return self.stipc.ping()

    def create_wayland_output(self):
        return self.stipc.create_wayland_output()

    def destroy_wayland_output(self, output: str):
        return self.stipc.destroy_wayland_output(output)

    def send_json(self, data):
        return self.sock.send_json(data)

    def list_outputs(self):
        return self.sock.list_outputs()

    def list_views(self):
        try:
            views = self.sock.list_views()
        except:
            # Support for older Wayfire versions (pre-0.8.1)
            message = get_msg_template("stipc/list_views")
            views = self.sock.send_json(message)

        for i in range(len(views)):
            for field in ['minimized', 'activated', 'focusable', 'mapped']:
                if 'state' in views[i] and field in views[i]['state']:
                    views[i][field] = views[i]['state'][field]
                elif field not in views[i]:
                    views[i][field] = False

            if 'output' in views[i]:
                views[i]['output-name'] = views[i]['output']

            if 'output' not in views[i]:
                views[i]['output'] = views[i]['output-name']

        return views

    def layout_views(self, layout):
        return self.stipc.layout_views(layout)

    def get_view_info(self, app_id: str, mapped_only: bool = False) -> Any:
        views = self.list_views()
        for v in views:
            if v['app-id'] == app_id and (not mapped_only or v['mapped']) :
                return v
        return None

    def get_view_info_title(self, title: str) -> Any:
        views = self.list_views()
        for v in views:
            if v['title'] == title:
                return v
        return None

    def get_view_info_id(self, id) -> Any:
        for v in self.list_views():
            if v['id'] == id:
                return v
        return None

    def run(self, cmd):
        return self.stipc.run_cmd(cmd)

    def move_cursor(self, x: int, y: int):
        return self.stipc.move_cursor(x, y)

    def set_touch(self, id: int, x: int, y: int):
        return self.stipc.set_touch(id, x, y)

    def release_touch(self, id: int):
        return self.stipc.release_touch(id)

    def click_button(self, btn_with_mod: str, mode: str):
        """
        btn_with_mod can be S-BTN_LEFT/BTN_RIGHT/etc. or just BTN_LEFT/...
        If S-BTN..., then the super modifier will be pressed as well.
        mode is full, press or release
        """
        return self.stipc.click_button(btn_with_mod, mode)

    def set_key_state(self, key: str, state: bool):
        return self.stipc.set_key_state(key, state)

    def press_key(self, key: str, pause: float = 0):
        return self.stipc.press_key(key, int(pause * 1000))

    def tablet_tool_proximity(self, x, y, prox_in):
        return self.stipc.tablet_tool_proximity(x, y, prox_in)

    def tablet_tool_tip(self, x, y, state):
        return self.stipc.tablet_tool_tip(x, y, state)

    def tablet_tool_axis(self, x, y, pressure):
        return self.stipc.tablet_tool_axis(x, y, pressure)

    def tablet_tool_button(self, btn, state):
        return self.stipc.tablet_tool_button(btn, state)

    def tablet_pad_button(self, btn, state):
        return self.stipc.tablet_pad_button(btn, state)

    def delay_next_tx(self):
        return self.stipc.delay_next_tx()

    def xwayland_pid(self):
        return self.stipc.xwayland_pid()

    def xwayland_display(self):
        return self.stipc.xwayland_display()

    def ipc_rules_get_focused(self):
        info = self.sock.get_focused_view()
        resp = info
        resp['info'] = info # backwards compatibility with older ipc lib implementations
        return resp

# Helper functions
def check_geometry(x: int, y: int, width: int, height: int, obj) -> bool:
    if obj['x'] == x and obj['y'] == y and \
        obj['width'] == width and obj['height'] == height:
        return True
    return False
