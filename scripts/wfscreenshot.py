#!/bin/env python3

from wfpyipc import wfipclib as wi
import sys
import os

if len(sys.argv) != 2:
    print("Invalid usage of wfscreenshot.py, use wfscreenshot.py <destination file>")
    sys.exit(-1)

socket = wi.open_socket()
msg = wi.get_msg_template()

pid = wi.run(socket, "grim " + sys.argv[1])
if not ("response", "ok") in pid.items():
    sys.exit(-1)
pid = pid["pid"]

try:
    os.waitpid(pid, 0)
except:
    pass
