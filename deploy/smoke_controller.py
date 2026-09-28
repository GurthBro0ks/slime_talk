#!/usr/bin/env python3
"""NUC2 live controller smoke test; prints only safe result labels.

Run with the isolated Python environment containing livekit==1.1.19:
  python deploy/smoke_controller.py /PRIVATE/PATH/devices.json

This creates two short-lived controller sessions. Restart the service afterward
to clear them. It never registers an APNs token or publishes media.
"""

import asyncio
import gc
import json
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from livekit import rtc


ORIGIN = "http://127.0.0.1:8787"


def post(path, body, session=None):
    headers = {"Content-Type": "application/json"}
    if session:
        headers["Authorization"] = "Bearer " + session
    request = urllib.request.Request(
        ORIGIN + path,
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, None


async def check(devices):
    assert post("/status", {})[0] == 401
    assert post("/login", {"device": "pixel", "key": "invalid"})[0] == 401
    print("AUTH_REJECTION=PASS", flush=True)

    pixel = post("/login", {"device": "pixel", "key": devices["pixel"]})
    iphone = post("/login", {"device": "iphone", "key": devices["iphone"]})
    assert pixel[0] == iphone[0] == 200
    assert pixel[1]["session"] != iphone[1]["session"]
    print("REAL_DEVICE_LOGIN=PASS", flush=True)

    rooms = [rtc.Room(), rtc.Room()]
    try:
        for room, login in zip(rooms, (pixel, iphone)):
            await asyncio.wait_for(room.connect(login[1]["url"], login[1]["token"]), 15)
            assert room.isconnected()
        print("HEADLESS_LIVEKIT_CONNECT=PASS", flush=True)

        p = pixel[1]["session"]
        i = iphone[1]["session"]
        assert post("/status", {}, p) == (200, {"busy": False, "owner": None, "epoch": None})
        grant = post("/request", {"requestId": str(uuid.uuid4())}, p)
        assert grant[0] == 200 and grant[1]["granted"] is True
        epoch = grant[1]["epoch"]
        assert post("/request", {"requestId": str(uuid.uuid4())}, i) == (200, {"granted": False})
        assert post("/renew", {"epoch": epoch}, p)[0] == 200
        assert post("/release", {"epoch": epoch}, p) == (200, {"released": True})
        grant2 = post("/request", {"requestId": str(uuid.uuid4())}, i)
        assert grant2[0] == 200 and grant2[1]["granted"] is True
        assert post("/release", {"epoch": epoch}, p)[0] == 409
        assert post("/release", {"epoch": grant2[1]["epoch"]}, i)[0] == 200
        print("ARBITRATION_AND_STALE_EPOCH=PASS", flush=True)

        grant3 = post("/request", {"requestId": str(uuid.uuid4())}, p)
        assert grant3[0] == 200 and grant3[1]["granted"] is True
        await asyncio.sleep(4.5)
        assert post("/status", {}, i) == (200, {"busy": False, "owner": None, "epoch": None})
        print("LEASE_EXPIRY=PASS", flush=True)
    finally:
        for room in rooms:
            if room.isconnected():
                await asyncio.wait_for(room.disconnect(), 10)
        print("HEADLESS_DISCONNECT=PASS", flush=True)


def main():
    devices = json.loads(Path(sys.argv[1]).read_text())
    assert set(devices) == {"pixel", "iphone"}
    asyncio.run(check(devices))
    # The SDK disposes its native FFI at interpreter exit. Collect room and
    # participant handles while that FFI is still alive.
    gc.collect()
    print("SDK_PRE_EXIT_GC=PASS", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("SMOKE=FAIL:" + type(error).__name__, file=sys.stderr)
        sys.exit(1)
