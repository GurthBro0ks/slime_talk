#!/usr/bin/env python3
"""Show one existing pairing key only in the owner's interactive terminal.

This helper is for later physical enrollment. Do not run it in CI, agent tools,
recorded terminals, or shared screens. It creates no new keys or files.
"""

import json
import os
from pathlib import Path
import stat
import sys


PRIVATE = Path("/home/slimy/.local/share/slime-talk-feasibility/devices.json")
ORIGIN = "https://slimy-nuc2.tailf64507.ts.net:8443"


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("pixel", "iphone"):
        raise SystemExit("Usage: python3 deploy/show_device_pairing.py pixel|iphone")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise SystemExit("Interactive private terminal required")
    st = PRIVATE.stat()
    if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o600:
        raise SystemExit("Private pairing file permissions are not 0600 for this user")
    devices = json.loads(PRIVATE.read_text())
    if set(devices) != {"pixel", "iphone"}:
        raise SystemExit("Private pairing file shape is invalid")
    selected = sys.argv[1]
    with open("/dev/tty", "w") as tty:
        tty.write("Controller HTTPS URL: " + ORIGIN + "\n")
        tty.write(selected.capitalize() + " pairing key: " + devices[selected] + "\n")
        tty.flush()


if __name__ == "__main__":
    main()
