#!/usr/bin/env python3
"""One-time, bounded NUC2 privileged gate. Prints no credential values.

Run only for the authorized temporary controller deployment. The result file
contains safe metadata so the unprivileged agent can inspect it afterward.
"""

import base64
import grp
import hashlib
import hmac
import json
import os
from pathlib import Path
import pwd
import re
import socket
import subprocess
import sys
import time
import urllib.request


REPO = Path("/home/slimy/projects/slime_talk")
PRIVATE = Path("/etc/slime-talk-feasibility")
RESULT = Path("/home/slimy/.local/share/slime-talk-feasibility/root-gate-result.json")
SERVICE = "slime-talk-feasibility.service"
ROOM = "slime-talk-feasibility"
checks = {}


def check(name, passed):
    checks[name] = "PASS" if passed else "FAIL"
    if not passed:
        raise RuntimeError(name)


def run(*args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    check("command_" + args[0].rsplit("/", 1)[-1], p.returncode == 0)
    return p.stdout


def permissions(path, user, group, mode):
    st = path.stat()
    return (
        pwd.getpwuid(st.st_uid).pw_name == user
        and grp.getgrgid(st.st_gid).gr_name == group
        and st.st_mode & 0o777 == mode
    )


def b64(data):
    return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()


def participants(env):
    now = int(time.time())
    head = b64({"alg": "HS256", "typ": "JWT"})
    payload = b64({
        "iss": env["LIVEKIT_API_KEY"], "sub": "controller-gate",
        "iat": now, "nbf": now - 5, "exp": now + 60,
        "video": {"roomAdmin": True, "room": ROOM, "roomList": True},
    })
    data = (head + "." + payload).encode()
    signature = base64.urlsafe_b64encode(hmac.new(env["LIVEKIT_API_SECRET"].encode(), data, hashlib.sha256).digest()).rstrip(b"=").decode()
    url = env["LIVEKIT_URL"].replace("wss://", "https://", 1).rstrip("/")
    request = urllib.request.Request(
        url + "/twirp/livekit.RoomService/ListParticipants",
        data=json.dumps({"room": ROOM}).encode(),
        headers={"Authorization": "Bearer " + data.decode() + "." + signature, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return len(json.load(response).get("participants", []))


def main():
    check("root_identity", os.geteuid() == 0)
    check("private_directory_permissions", permissions(PRIVATE, "root", "slime-talk", 0o750))
    check("environment_permissions", permissions(PRIVATE / "controller.env", "root", "root", 0o600))
    check("apns_permissions", permissions(PRIVATE / "apns.p8", "root", "slime-talk", 0o640))
    check("devices_permissions", permissions(PRIVATE / "devices.json", "root", "slime-talk", 0o640))
    check("source_directory_permissions", permissions(Path("/opt/slime-talk-feasibility"), "root", "root", 0o755))

    installed = Path("/opt/slime-talk-feasibility/controller")
    check("installed_source_match", all(
        (REPO / "controller" / name).read_bytes() == (installed / name).read_bytes()
        for name in ("server.mjs", "core.mjs", "adapters.mjs", "package.json")
    ))
    check("installed_unit_match", (REPO / "deploy/slime-talk-feasibility.service").read_bytes()
          == Path("/etc/systemd/system/slime-talk-feasibility.service").read_bytes())

    env = {}
    for line in (PRIVATE / "controller.env").read_text().splitlines():
        if line and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"')
    devices = json.loads((PRIVATE / "devices.json").read_text())
    check("device_config_shape", set(devices) == {"pixel", "iphone"})
    check("media_config_shape", all(env.get(k) for k in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")))

    run("/usr/bin/systemctl", "restart", SERVICE)
    state = run("/usr/bin/systemctl", "show", SERVICE, "-p", "ActiveState", "-p", "NRestarts", "-p", "MainPID")
    fields = dict(line.split("=", 1) for line in state.splitlines() if "=" in line)
    check("service_active", fields.get("ActiveState") == "active" and int(fields.get("MainPID", "0")) > 0)
    check("service_no_restarts", fields.get("NRestarts") == "0")
    listener_ready = False
    for _ in range(20):
        try:
            with socket.create_connection(("127.0.0.1", 8787), timeout=1):
                listener_ready = True
                break
        except OSError:
            time.sleep(0.5)
    check("loopback_listener", listener_ready)
    check("livekit_participants_cleared", participants(env) == 0)

    logs = run("/usr/bin/journalctl", "-u", SERVICE, "--since", "2026-09-28 16:50:00", "--no-pager", "-o", "cat")
    values = list(devices.values()) + [env["LIVEKIT_API_KEY"], env["LIVEKIT_API_SECRET"], (PRIVATE / "apns.p8").read_text()]
    check("known_secret_log_scan", not any(value and value in logs for value in values))
    check("jwt_log_scan", re.search(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", logs) is None)
    check("private_key_marker_log_scan", "PRIVATE KEY-----" not in logs)


if __name__ == "__main__":
    try:
        main()
        status = "PASS"
    except Exception:
        status = "FAIL"
    RESULT.write_text(json.dumps({"status": status, "checks": checks}, sort_keys=True) + "\n")
    RESULT.chmod(0o644)
    print("NUC2_ROOT_GATE=" + status)
    for name, result in checks.items():
        print(name.upper() + "=" + result)
    sys.exit(0 if status == "PASS" else 1)
