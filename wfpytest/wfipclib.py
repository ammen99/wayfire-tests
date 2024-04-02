from typing import Any
import socket
import json as js
import select

def get_msg_template(cmd: str | None = None):
    # Create generic message template
    message = {}
    message["data"] = {}
    if str is not None:
        message["method"] = cmd
    return message

class WayfireIPCClient:
    def __init__(self, socket_name: str):
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.client.connect(socket_name)
        self.client.setblocking(False)

    def read_exact(self, n, timeout: float | None = None):
        response = bytes()
        while n > 0:
            ready = select.select([self.client], [], [], 5 if timeout is None else timeout) # Wait 5 seconds
            if not ready[0]:
                if timeout is None:
                    raise Exception("Failed to read from socket: timeout")
                else:
                    return None

            read_this_time = self.client.recv(n)
            if not read_this_time:
                raise Exception("Failed to read anything from the socket!")
            n -= len(read_this_time)
            response += read_this_time

        return response

    def read_message(self, timeout: float = 5):
        length = self.read_exact(4, timeout)
        if not length:
            return None

        rlen = int.from_bytes(length, byteorder="little")
        response_message = self.read_exact(rlen)
        assert response_message is not None
        return js.loads(response_message)

    def _send_json(self, msg):
        data = js.dumps(msg).encode('utf8')
        header = len(data).to_bytes(4, byteorder="little")
        self.client.send(header)
        self.client.send(data)
        resp = self.read_message()
        assert resp is not None
        return resp

    def send_json(self, msg):
        response = self._send_json(msg)
        if 'error' in response:
            msg["method"] = "core" + msg["method"][5:]
            response2 = self._send_json(msg)
            if 'error' in response2:
                return response
            return response2
        return response

    def ping(self):
        message = get_msg_template()
        message["method"] = "stipc/ping"
        response = self.send_json(message)
        return ("result", "ok") in response.items()

    def create_wayland_output(self):
        message = get_msg_template()
        message["method"] = "stipc/create_wayland_output"
        self.send_json(message)

    def destroy_wayland_output(self, output: str):
        message = get_msg_template()
        message["method"] = "stipc/destroy_wayland_output"
        message["data"]["output"] = output
        return self.send_json(message)

    def list_outputs(self):
        message = get_msg_template("window-rules/list-outputs")
        return self.send_json(message)

    def list_views(self):
        message = get_msg_template()
        message["method"] = "stipc/list_views"
        views = self.send_json(message)
        if "error" in views:
            message["method"] = "window-rules/list-views"
            views = self.send_json(message)

        # Support for older Wayfire versions (pre-0.8.1)
        for i in range(len(views)):
            for field in ['minimized', 'activated', 'focusable', 'mapped']:
                if 'state' in views[i] and field in views[i]['state']:
                    views[i][field] = views[i]['state'][field]
                elif field not in views[i]:
                    views[i][field] = False

            if 'output' in views[i]:
                views[i]['output-name'] = views[i]['output']

        return views

    def layout_views(self, layout):
        views = self.list_views()
        message = get_msg_template()
        message["method"] = "stipc/layout_views"
        msg_layout = []

        for ident in layout:
            x, y, w, h = layout[ident][:4]
            for v in views:
                if v['app-id'] == ident or v['title'] == ident or v['id'] == ident:
                    layout_for_view = {"id": v["id"], "x": x, "y": y, "width": w, "height": h}
                    if len(layout[ident]) == 5:
                        layout_for_view["output"] = layout[ident][-1]
                    msg_layout.append(layout_for_view)

        message["data"]["views"] = msg_layout
        return self.send_json(message)

    def get_view_info(self, app_id: str, mappedOnly: bool = False) -> Any:
        views = self.list_views()
        for v in views:
            if v['app-id'] == app_id and (not mappedOnly or v['mapped']) :
                return v
        return None

    def get_view_info_title(self, title: str) -> Any:
        views = self.list_views()
        for v in views:
            if v['title'] == title:
                return v
        return None

    def get_view_info_id(self, id):
        for v in self.list_views():
            if v['id'] == id:
                return v
        return None

    def run(self, cmd):
        message = get_msg_template()
        message["method"] = "stipc/run"
        message["data"]["cmd"] = cmd
        return self.send_json(message)

    def move_cursor(self, x: int, y: int):
        message = get_msg_template()
        message["method"] = "stipc/move_cursor"
        message["data"]["x"] = x
        message["data"]["y"] = y
        return self.send_json(message)

    def set_touch(self, id: int, x: int, y: int):
        message = get_msg_template()
        message["method"] = "stipc/touch"
        message["data"]["finger"] = id
        message["data"]["x"] = x
        message["data"]["y"] = y
        return self.send_json(message)

    def release_touch(self, id: int):
        message = get_msg_template()
        message["method"] = "stipc/touch_release"
        message["data"]["finger"] = id
        return self.send_json(message)

    def click_button(self, btn_with_mod: str, mode: str):
        """
        btn_with_mod can be S-BTN_LEFT/BTN_RIGHT/etc. or just BTN_LEFT/...
        If S-BTN..., then the super modifier will be pressed as well.
        mode is full, press or release
        """
        message = get_msg_template()
        message["method"] = "stipc/feed_button"
        message["data"]["mode"] = mode
        message["data"]["combo"] = btn_with_mod
        return self.send_json(message)

    def set_key_state(self, key: str, state: bool):
        message = get_msg_template()
        message["method"] = "stipc/feed_key"
        message["data"]["key"] = key
        message["data"]["state"] = state
        return self.send_json(message)

    def press_key(self, key: str):
        if key[:2] == 'S-':
            self.set_key_state('KEY_LEFTMETA', True)
            self.set_key_state(key[2:], True)
            self.set_key_state(key[2:], False)
            self.set_key_state('KEY_LEFTMETA', False)
        elif key[:2] == 'C-':
            self.set_key_state('KEY_LEFTCTRL', True)
            self.set_key_state(key[2:], True)
            self.set_key_state(key[2:], False)
            self.set_key_state('KEY_LEFTCTRL', False)
        elif key[:2] == 'A-':
            self.set_key_state('KEY_LEFTALT', True)
            self.set_key_state(key[2:], True)
            self.set_key_state(key[2:], False)
            self.set_key_state('KEY_LEFTALT', False)
        else:
            self.set_key_state(key, True)
            self.set_key_state(key, False)

    def tablet_tool_proximity(self, x, y, prox_in):
        message = get_msg_template()
        message["method"] = "stipc/tablet/tool_proximity"
        message["data"]["x"] = x
        message["data"]["y"] = y
        message["data"]["proximity_in"] = prox_in
        return self.send_json(message)

    def tablet_tool_tip(self, x, y, state):
        message = get_msg_template()
        message["method"] = "stipc/tablet/tool_tip"
        message["data"]["x"] = x
        message["data"]["y"] = y
        message["data"]["state"] = state
        return self.send_json(message)

    def tablet_tool_axis(self, x, y, pressure):
        message = get_msg_template()
        message["method"] = "stipc/tablet/tool_axis"
        message["data"]["x"] = x
        message["data"]["y"] = y
        message["data"]["pressure"] = pressure
        return self.send_json(message)

    def tablet_tool_button(self, btn, state):
        message = get_msg_template()
        message["method"] = "stipc/tablet/tool_button"
        message["data"]["button"] = btn
        message["data"]["state"] = state
        return self.send_json(message)

    def tablet_pad_button(self, btn, state):
        message = get_msg_template()
        message["method"] = "stipc/tablet/pad_button"
        message["data"]["button"] = btn
        message["data"]["state"] = state
        return self.send_json(message)

    def delay_next_tx(self):
        message = get_msg_template()
        message["method"] = "stipc/delay_next_tx"
        return self.send_json(message)

    def xwayland_pid(self):
        message = get_msg_template()
        message["method"] = "stipc/get_xwayland_pid"
        return self.send_json(message)

    def xwayland_display(self):
        message = get_msg_template()
        message["method"] = "stipc/get_xwayland_display"
        return self.send_json(message)

    def ipc_rules_get_focused(self):
        message = get_msg_template()
        message["method"] = "window-rules/get-focused-view"
        return self.send_json(message)

# Helper functions
def check_geometry(x: int, y: int, width: int, height: int, obj) -> bool:
    if obj['x'] == x and obj['y'] == y and \
        obj['width'] == width and obj['height'] == height:
        return True
    return False
