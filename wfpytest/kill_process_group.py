import os
import signal
import sys
import time

pgid = int(sys.argv[1])
try:
    time.sleep(0.5)
    os.killpg(pgid, signal.SIGKILL)
except:
    pass
