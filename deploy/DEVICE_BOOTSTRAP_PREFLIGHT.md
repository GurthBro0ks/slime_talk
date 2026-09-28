# Device bootstrap preflight — 2026-09-28

Scope: enrollment and connectivity only. Physical Pixel interaction, cellular-path verification, PTT, capture, publication, APNs delivery, and F1–F7 acceptance remain outside this preflight.

## Safe infrastructure state

- `slime-talk-feasibility.service`: active/running since 17:07:32 UTC, `NRestarts=0`, unit disabled for boot startup. No service action was taken during this preflight.
- Controller listener: `127.0.0.1:8787` only. Local unauthenticated `POST /status`: HTTP 401.
- Tailscale Funnel: HTTPS 8443 -> `http://127.0.0.1:8787`; unauthenticated `POST /status` through the public HTTPS origin: HTTP 401. Existing HTTPS 443 -> `http://127.0.0.1:8080` remained in place. No Funnel change was made.
- Git: `origin/main` fetched to `4a65a7d1790e4df3d478617a983376c559d324ff` without changing the local checkout or its files during the fetch.

## Real Pixel observation plan

The owner must enter the existing Pixel-only pairing credential in the app using the private interactive helper documented in `deploy/README.md`; agents must not run that helper. The owner performs the phone login and states whether the phone was on cellular. No agent claims that network-path fact from the NUC.

The controller creates a fresh random UUID for each successful login. It puts that UUID in the LiveKit JWT `sub` claim and grants `roomJoin=true`, `canSubscribe=true`, `canPublish=false`, and `canPublishData=false`. A read-only LiveKit `ListParticipants` query using the root-owned LiveKit credentials can identify a newly joined participant and check its receive-only permission. Keep the JWT, credentials, and raw API response private. Report only the number of newly joined participants, a short digest of the UUID, and PASS/FAIL permission fields. The current app and controller logs do not expose the token `sub`; matching a participant to the Pixel by a single join time window is an inference, and is inconclusive if multiple clients join concurrently. An exact identity match would require a private, owner-controlled reading of the Pixel's issued token claim. Do not interrupt or relog an existing client to force a match.

The Android app starts `/status` polling every 500 ms after LiveKit connects. Any failed status request triggers `controller_connection_loss` and leaves the connected state. The owner may provide a sanitized QA trace showing `media_connected`, continued `IDLE` after several poll intervals, and no `controller_connection_loss` in that window. This supports successful status polling but does not expose individual HTTP 200 responses: the current server does not log successful `/status` requests, and the app does not log them either. Mark direct per-request status proof `UNVERIFIED` unless an owner-controlled passive observer records only response codes and correlates the session internally. Do not make a second Pixel login from an agent: it would invalidate the phone's session.

Current observation state: `READY_FOR_OWNER_PHONE_ACTION_WITH_LIMITS`; positive login, receive-only real Pixel participation, and authenticated status polling are not yet verified. Root-owned media credentials are unavailable to the unprivileged agent (`sudo -n` denied), so the read-only participant query requires the owner's privileged session. No raw authentication response should enter terminal output or a report.

## Apple diagnostic

Commit `4a65a7d1790e4df3d478617a983376c559d324ff` adds `.github/workflows/testflight-build16-diagnostic.yml`. The push-triggered run exists: https://github.com/GurthBro0ks/slime_talk/actions/runs/36458087255. At 17:34 UTC it was `waiting` for the existing `ios-feasibility-signing` required-owner-review environment. No manual dispatch, deployment approval, signing/upload run, or build upload was performed.

The workflow makes GET requests to Apple's app `6816454718`, filters version `0.1.0` build `16`, suppresses sensitive exception details, and reports allowlisted metadata. The existing environment has required reviewer `GurthBro0ks` and `can_admins_bypass=false`; no protection change was made.

## Verification

- `systemctl show slime-talk-feasibility.service -p ActiveState -p SubState -p UnitFileState -p MainPID -p NRestarts -p ActiveEnterTimestamp`
- `ss -H -ltnp 'sport = :8787'`
- `tailscale serve status --json` and `tailscale funnel status --json`
- Local and Funnel unauthenticated `POST /status` HTTP-code checks: both 401.
- `gh run list` and `gh run view` for diagnostic run `36458087255`; GitHub pending-deployments API and environment protection API.
- `python3 ci/security_check.py`: PASS; `node --test controller/test/*.mjs`: 12/12 PASS; `git diff --check`: PASS.

PREFLIGHT=PASS. Owner phone action and the existing GitHub review gate are pending. These are separate gates; neither is implied to have passed by this preflight.
