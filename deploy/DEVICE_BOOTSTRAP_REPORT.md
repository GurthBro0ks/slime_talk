# SLIME_TALK_DEVICE_BOOTSTRAP_001

Observed 2026-09-28, approximately 17:50–17:57 UTC. Scope: Phase 0 Gate 0C enrollment/connectivity only.

RESULT=BLOCKED
READY_FOR_PHYSICAL_QA=no

## PASS — infrastructure and candidate

- Desktop-to-NUC2 SSH alias `nuc2` resolves to `slimy-nuc2`. NUC2 repository `/home/slimy/projects/slime_talk` started clean at `81b09f1`, with one worktree. The desktop project directory was empty, not a Git checkout. Existing NUC2 work was preserved.
- Service active/running, boot startup disabled, NRestarts=0. Listener only `127.0.0.1:8787`. No service, firewall, or Funnel mutations.
- Funnel HTTPS 8443 maps to `http://127.0.0.1:8787`; unrelated HTTPS 443 maps to `http://127.0.0.1:8080`, preserved.
- Local and desktop-origin public HTTPS `POST /status` with JSON `{}` returned HTTP 401. An initial empty-body public POST returned 400; it was not counted as authentication proof. Desktop HTTPS is not Pixel cellular evidence.
- USB ADB identified model Pixel 6 Pro, product/device raven. Private USB identifier omitted from this report. The app package was absent before installation.
- Existing Actions run 36334126880, artifact `slime-talk-feasibility-apk` (artifact ID 10936767938), downloaded without rebuilding. APK SHA-256 exactly `7a3d3b9b6a2e6f836fec73e7584ff178a824dcf26add76ca5fd99a151dbce065`.
- Binary APK manifest independently parsed: package `ai.slimy.slimetalk.feasibility`, version `0.1.0`, versionCode `4`, minSdk 30, targetSdk 35, allowBackup false, usesCleartextTraffic false. ADB installation succeeded; installed package metadata independently confirmed version 0.1.0/build 4. No uninstall or app-data erasure.

## BLOCKED — cellular route and private enrollment

- Wi-Fi initially enabled; temporarily disabled (`wifi_on=0`). Mobile data enabled, airplane mode off, SIM state LOADED. Tailscale is installed and was force-stopped for the route check.
- Current connectivity then reported `Active default network: none`, no current network agents, data connection state 0, and data enabled true. Historical network request entries were excluded as route evidence.
- Owner explicitly confirmed: “there is no cell data on this phone”. The required cellular route therefore cannot be exercised. No Wi-Fi, tethering, proxy, or ADB reverse substitute was used.
- Private pairing was not begun. The pairing-display helper was never executed by the agent; no key was read or entered. The app's reviewed source uses Android Keystore AES-GCM protection; actual storage of a real credential remains UNVERIFIED.
- App safely force-stopped, process absence checked, and original Wi-Fi enabled state restored (`wifi_on=1`). Tailscale was not relaunched. No Join/reconnect or HOLD TO TALK interaction occurred.

## UNVERIFIED — authentication, status, identity and audio

- Real Pixel positive authentication, authenticated public status retrieval, receive-only LiveKit connection, and exact controller/LiveKit pseudonymous identity: UNVERIFIED because no enrollment/login occurred.
- Continued unauthenticated rejection: PASS for local and desktop public JSON status requests, not a phone-session proof.
- No second Pixel login, wrong-device credential experiment, controller session replacement, APNs test push, PTT, arbitration, silence-timeout, microphone activation, or audio publication was requested.
- Microphone permission remained denied (`RECORD_AUDIO granted=false`; app-op ignore). Filtered SLIME_PTT event-name counts were empty. No unexpected microphone/audio activity was observed during install/launch/close; receive-only runtime capture/publication behavior was NOT TESTED. Permission state is not itself a full capture audit.
- Controller observation is limited to service/listener/routing/rejection checks. No new participant observation or exact identity correlation is claimed. Existing preflight explains that current app/controller logs cannot directly prove individual successful status responses or exact phone token identity.

## SLIME_TALK_TESTFLIGHT_DIAGNOSTIC_001

- App 6816454718, version 0.1.0, build 16 unchanged. Original run 36458087255 completed failure: APP_ID_MATCH=true; upload-list GET returned 403; no build-resource state established.
- Apple documents this GET endpoint and a 403 response: https://developer.apple.com/documentation/appstoreconnectapi/get-v1-apps-_id_-builduploads . The HTTP status alone does not establish the precise permission cause.
- Diagnostic-only commit `710ab5b94563425d8f4a9694c5a31ff4b0fecf23` continues an independent build-record GET after upload-list failure. It emits allowlisted error codes and reason booleans, never raw Apple error detail. Unavailable results are null, not false zero-match claims. Legal/agreement/export-compliance indicators stop the diagnostic. Existing credentials, endpoint-scoped GET JWTs, environment protections, and no-upload behavior are preserved.
- Validation: YAML parse, embedded JavaScript syntax, mock 403 proving independent build query plus sensitive-detail suppression, tracked-source security check, and git diff check PASS. Existing controller unit tests 12/12 PASS; those tests are not physical acceptance.
- Owner-reviewed diagnostic run https://github.com/GurthBro0ks/slime_talk/actions/runs/36461341386 completed at 17:54:59 UTC. Both upload-list and independent build-list GETs returned HTTP 403 with exact allowlisted code `FORBIDDEN.REQUEST_DOES_NOT_MATCH_SCOPE`. APP_ID_MATCH=true. No agreement-action indicator was detected. This establishes a token/request scope mismatch, not a build-processing state or insufficient API-key role.
- Apple documents query matching at https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests . Follow-up commit `32bf739` includes the exact query string in each GET-only token scope. Mock validation verifies that the decoded synthetic JWT scope equals the requested path and query. No API-key permission expansion or unscoped token. Run https://github.com/GurthBro0ks/slime_talk/actions/runs/36461641716 awaits the same owner-required environment review; no agent approval/bypass.
- 403 reason is verified as request/token scope mismatch. Upload record/state, build resource/processing state, and TestFlight visibility/installability remain UNVERIFIED pending the corrected protected run. No PROCESSING-over-24-hours assertion is justified. No new signing/upload, key creation/rotation, or permission expansion. iPhone enrollment not prepared because an installable internal build has not been established.

## Secret exposure

No pairing, LiveKit/API/APNs secret or Apple credential/token was read into agent output, commands, reports, or screenshots. No phone screenshot or UI-field dump was taken. This is a scoped handling statement, not a comprehensive historical secret audit. Raw device identifiers are omitted from this committed report.

## Blockers and recommended next action

1. Required Pixel cellular service is absent. Owner must provide cellular data on this Pixel or obtain a canonical PM decision changing the work order before a different route may count.
2. Owner must review the existing protected diagnostic run; then inspect sanitized results and independently establish TestFlight visibility. If confirmed PROCESSING beyond 24 hours, mark blocked for Apple escalation. Upload age alone is insufficient.
3. After cellular service is available, perform private owner-only pairing, bounded receive-only observation and safe disconnect. Keep identity/status evidence limits explicit. Production implementation and physical F1–F7/PTT acceptance remain NOT AUTHORIZED.
