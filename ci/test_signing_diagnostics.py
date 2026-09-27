#!/usr/bin/env python3
"""Run offline tests of the workflow's allowlisted metadata classifier.
No Apple/GitHub credentials, macOS tools, or third-party packages are needed.
"""
import ast
import datetime
import pathlib
import textwrap

workflow = pathlib.Path(__file__).resolve().parents[1] / ".github/workflows/ios-signing-probe.yml"
source = workflow.read_text().split("          python3 -I - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
tree = ast.parse(textwrap.dedent(source))
names = {"ptt_state", "apns_state", "id_state", "profile_type", "expiry_state", "safe_diagnostic"}
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
assert {node.name for node in functions} == names
namespace = {"datetime": datetime}
exec(compile(ast.Module(body=functions, type_ignores=[]), "<metadata-classifier>", "exec"), namespace)
entitlements = {
    "com.apple.developer.push-to-talk": True,
    "aps-environment": "production",
    "application-identifier": "TESTTEAM01.ai.slimy.slimetalk.feasibility",
    "com.apple.developer.team-identifier": "TESTTEAM01",
    "get-task-allow": False,
    "beta-reports-active": True,
}
profile = {
    "Entitlements": entitlements.copy(),
    "TeamIdentifier": ["TESTTEAM01"],
    "ExpirationDate": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
}
def inspect(app, permitted):
    return namespace["safe_diagnostic"](app, permitted, "TESTTEAM01", "ai.slimy.slimetalk.feasibility")

assert inspect(entitlements, profile)["SIGNED_APP_PTT_ENTITLEMENT"] == "present"
assert inspect({}, profile)["SIGNED_APP_PTT_ENTITLEMENT"] == "missing"
assert inspect(entitlements, {"Entitlements": {}})["PROFILE_PTT_ENTITLEMENT"] == "missing"
assert inspect(dict(entitlements, **{"com.apple.developer.push-to-talk": 1}), profile)["SIGNED_APP_PTT_ENTITLEMENT"] == "unexpected"
assert inspect(dict(entitlements, **{"aps-environment": "development"}), profile)["SIGNED_APP_APNS"] == "development"
assert inspect(entitlements, profile)["PROFILE_TYPE"] == "app-store"
assert inspect(entitlements, dict(profile, ProvisionedDevices=["synthetic"], Entitlements=dict(entitlements, **{"get-task-allow": True})))["PROFILE_TYPE"] == "development"
assert inspect(entitlements, dict(profile, ProvisionedDevices=["synthetic"]))["PROFILE_TYPE"] == "adhoc"
assert inspect(entitlements, dict(profile, ProvisionsAllDevices=True))["PROFILE_TYPE"] == "enterprise"
assert inspect(entitlements, {"Entitlements": {}})["PROFILE_TYPE"] == "unknown"
assert inspect(entitlements, dict(profile, ExpirationDate=datetime.datetime(2000, 1, 1)))["PROFILE_EXPIRY"] == "expired"
assert inspect(entitlements, {"Entitlements": {}})["PROFILE_EXPIRY"] == "unknown"
assert inspect({}, profile)["SIGNED_APP_NON_DEBUG"] == "no"
assert inspect(dict(entitlements, **{"application-identifier": "wrong"}), profile)["SIGNED_APP_APP_ID"] == "mismatch"
assert inspect(entitlements, dict(profile, TeamIdentifier=["wrong"]))["PROFILE_TEAM_METADATA"] == "mismatch"
canary = "DO_NOT_EMIT_CANARY"
assert canary not in str(inspect(dict(entitlements, private=canary), dict(profile, private=canary)))
print("PASS: 16 synthetic diagnostic/security cases; embedded Python syntax valid.")
