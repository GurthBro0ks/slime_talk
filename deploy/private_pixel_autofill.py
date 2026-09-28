#!/usr/bin/env python3
"""Owner-only USB field entry. Never run from agent tools or recorded terminals.

SSH stdout is captured in memory. ADB receives field text on stdin, never in
host command arguments. No screenshot, clipboard, file, login, or PTT action.
"""
import json
import os
import re
import resource
import shlex
import subprocess
import sys

ORIGIN = 'https://slimy-nuc2.tailf64507.ts.net:8443'
REMOTE_READER = '''import json,os,stat,sys
from pathlib import Path
p=Path('/home/slimy/.local/share/slime-talk-feasibility/devices.json')
s=p.lstat()
if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o600:
 sys.exit(1)
d=json.loads(p.read_text())
if set(d)!={'pixel','iphone'}: sys.exit(1)
sys.stdout.write(json.dumps(d['pixel']))
'''


def run(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=30)
    if result.returncode:
        raise RuntimeError('Private operation failed')
    return result.stdout


def field_commands(value):
    # Restrict input to characters that Android input text transmits literally.
    if not re.fullmatch(r'[A-Za-z0-9_:/\.\-]+', value):
        raise ValueError('Unsupported field characters')
    return ('set +x\ninput keyevent KEYCODE_MOVE_END\n' +
            'input keyevent ' + ' '.join(['KEYCODE_DEL'] * 512) + '\n' +
            'input text ' + shlex.quote(value) + '\nexit\n').encode()


def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError('Private interactive terminal required')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if run(['adb', 'get-state']).strip() != b'device':
        raise RuntimeError('One authorized USB device required')
    if run(['adb', 'shell', 'getprop', 'ro.product.model']).strip() != b'Pixel 6 Pro':
        raise RuntimeError('Pixel 6 Pro required')
    print('Open Slime Talk. Keep the phone on its enrollment screen.')
    print('Do not share or record this terminal or the phone screen.')
    input('Tap the controller URL field on the phone, then press Enter here: ')
    run(['adb', 'shell', '-T'], field_commands(ORIGIN))
    input('Tap the Pixel pairing-key field on the phone, then press Enter here: ')
    # This command contains source code, never a credential. SSH output stays in RAM.
    key = json.loads(run(['ssh', '-T', '-o', 'BatchMode=yes', 'nuc2',
                         'python3 -c ' + shlex.quote(REMOTE_READER)]))
    if not isinstance(key, str) or not 32 <= len(key) <= 256:
        raise RuntimeError('Unexpected private key format')
    run(['adb', 'shell', '-T'], field_commands(key))
    del key
    print('Fields filled. Tap Join / reconnect yourself. Do not press HOLD TO TALK.')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt):
        print('Autofill stopped. Private error details suppressed; no automatic retry.')
        sys.exit(1)
