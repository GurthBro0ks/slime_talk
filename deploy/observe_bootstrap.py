#!/usr/bin/env python3
"""Owner-run read-only evidence. No login, restart, audio, or secret output."""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request
import urllib.error


def observe():
    if os.geteuid() != 0:
        raise RuntimeError('owner_privileged_terminal_required')
    root = Path('/etc/slime-talk-feasibility')
    env = {}
    for line in (root / 'controller.env').read_text().splitlines():
        if line and not line.lstrip().startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"')
    now = int(time.time())
    enc = lambda v: base64.urlsafe_b64encode(json.dumps(v, separators=(',', ':')).encode()).rstrip(b'=').decode()
    raw = enc({'alg': 'HS256', 'typ': 'JWT'}) + '.' + enc({
        'iss': env['LIVEKIT_API_KEY'], 'sub': 'bootstrap-read-only-observer',
        'iat': now, 'nbf': now - 5, 'exp': now + 60,
        'video': {'roomAdmin': True, 'room': 'slime-talk-feasibility'},
    })
    token = raw + '.' + base64.urlsafe_b64encode(hmac.new(env['LIVEKIT_API_SECRET'].encode(), raw.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
    url = env['LIVEKIT_URL'].replace('wss://', 'https://', 1).rstrip('/')
    if not url.startswith('https://'):
        raise RuntimeError('https_required')
    req = urllib.request.Request(url + '/twirp/livekit.RoomService/ListParticipants',
        data=b'{"room":"slime-talk-feasibility"}',
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method='POST')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=10) as response:
            participants = json.load(response).get('participants', [])
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        participants = []
    result = {'observed_at_unix': now, 'participant_count': len(participants), 'participants': []}
    for p in participants:
        permission = p.get('permission', {})
        identity = p.get('identity', '')
        result['participants'].append({
            'identity_digest': hashlib.sha256(identity.encode()).hexdigest()[:16],
            'uuid_identity': bool(re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', identity)),
            'can_subscribe': permission.get('canSubscribe', False),
            'can_publish': permission.get('canPublish', False),
            'can_publish_data': permission.get('canPublishData', False),
            'published_track_count': len(p.get('tracks', [])),
        })
    logs = subprocess.check_output(['journalctl', '-u', 'slime-talk-feasibility.service', '--since', '2026-09-28 19:00:00 UTC', '--no-pager', '-o', 'cat'], text=True, stderr=subprocess.DEVNULL)
    values = list(json.loads((root / 'devices.json').read_text()).values()) + [env['LIVEKIT_API_KEY'], env['LIVEKIT_API_SECRET']]
    result['controller_known_secret_scan'] = 'FAIL' if any(v and v in logs for v in values) or re.search(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|PRIVATE KEY-----', logs) else 'PASS'
    result['identity_correlation'] = 'timing_only; exact_phone_session_not_exposed'
    return result


if __name__ == '__main__':
    try:
        output = observe()
    except Exception:
        output = {'result': 'BLOCKED', 'reason': 'private_observation_failed; details_suppressed'}
    path = Path('/home/slimy/.local/share/slime-talk-feasibility/bootstrap-observation.json')
    # Refuse symlinks and never store credentials or raw responses.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'w') as f:
        f.write(json.dumps(output, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))
