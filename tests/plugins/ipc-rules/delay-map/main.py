#!/bin/env python3

import wftest as wt

def is_gui() -> bool:
    return False

class WTest(wt.WayfireTest):
    def prepare(self):
        return self.require_test_clients(['weston-terminal'])

    def _run(self):
        ev_socket = self.watch(['view-pre-map', 'view-mapped'])
        self.socket.run('weston-terminal --shell=/bin/sh')

        ev = ev_socket.read_message(self._ipc_duration * 2)
        id: int = ev['view']['id'] # type: ignore

        data = self.socket.get_view_info_id(id)
        if data['mapped']:
            return wt.Status.WRONG, "View mapped too early!"
        if ev_socket.read_message(0.1):
            return wt.Status.WRONG, "Received unexpected event!"

        self.socket.sock.configure_view(id, 123, 135, 400, 300)
        self.socket.sock.unblock_view_map(id)
        map_msg = ev_socket.read_message(self._ipc_duration * 2)
        if not map_msg:
            return wt.Status.WRONG, "No view-mapped event after unblock!"

        if not map_msg['view']['mapped']: # type: ignore
            return wt.Status.WRONG, "View not mapped after unblock!"

        if map_msg['view']['geometry']['x'] != 123 or map_msg['view']['geometry']['y'] != 135: # type: ignore
            return wt.Status.WRONG, "View geometry incorrect after map!"

        return wt.Status.OK, None
