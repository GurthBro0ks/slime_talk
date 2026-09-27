#!/usr/bin/env python3
"""Check tracked mobile/config source for accidental embedded server credentials."""
from pathlib import Path
import re,subprocess
root=Path(__file__).resolve().parents[1]
errors=[]
paths=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines()
for name in paths:
 p=root/name
 if not p.is_file() or p.suffix in ['.jar','.png']:continue
 text=p.read_text(errors='replace')
 if re.search(r'-----BEGIN (?:EC |RSA )?PRIVATE KEY-----\s+[A-Za-z0-9+/]{30}',text):errors.append(name)
 if re.search(r'\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',text):errors.append(name)
 if name.startswith(('ios/','android/')) and any(x in text for x in ['LIVEKIT_API_SECRET','APNS_AUTH_KEY_P8','ASC_API_KEY_P8','BEGIN PRIVATE KEY']):errors.append(name)
assert not errors,'Credential boundary violation in: '+', '.join(sorted(set(errors)))
print('PASS: tracked source credential boundary checks (not a comprehensive secret audit)')
