import os
import socket
import json as js

def open_socket():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(str(os.getenv("WAYFIRE_SOCKET")))
    return client

def get_msg_template():
    # Create generic message template
    message = {}
    message["data"] = {}
    return message

def send_json(sock, msg):
    data = js.dumps(msg).encode('utf8')
    header = len(data).to_bytes(4, byteorder="little")
    sock.send(header)
    sock.send(data)

    response = sock.recv(1024)
    rlen = int.from_bytes(response[:4], byteorder="little")
    rps = js.loads(response[4:(rlen+4)])
    return rps

def create_wayland_output(socket):
    message = get_msg_template()
    message["method"] = "core/create_wayland_output"
    send_json(socket, message)

def list_views(socket, message):
    message = get_msg_template()
    message["method"] = "core/list_views"
    return send_json(socket, message)
