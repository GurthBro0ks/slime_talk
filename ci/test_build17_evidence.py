"""Offline guard checks: no credentials or Apple calls."""
import ast
from pathlib import Path
import re
s=Path('ci/build17_sign.py').read_text()
ast.parse(s)
assert s.count("'--upload-app'")==1
assert "'CURRENT_PROJECT_VERSION=17'" in s
assert "os.environ.get('GITHUB_RUN_ATTEMPT') != '1'" in s
assert s.index("Exact version/build verification failed") < s.index("'--upload-app'")
assert s.index("Production APNs entitlement is missing") < s.index("'--upload-app'")
assert s.index("Provisioning profile is expired") < s.index("'--upload-app'")
tree=ast.parse(s)
fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='find_request_id')
ns={'re':re,'request_ids':set()}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<request-id-filter>','exec'),ns)
u='12345678-1234-1234-1234-123456789abc'
ns['find_request_id']({'request-id':u,'token':'DO_NOT_EMIT_CANARY','id':'unrelated'})
assert ns['request_ids']=={u}
ns['request_ids'].clear()
ns['find_request_id']({'request-id':'DO_NOT_EMIT_CANARY','delivery-id':u,'id':u})
assert not ns['request_ids']
print('PASS: build 17 syntax, fixed-build, single-upload, verification ordering, request-ID allowlist')
