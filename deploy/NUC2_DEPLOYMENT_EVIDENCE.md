# SLIME_TALK_CONTROLLER_DEPLOY_001 — NUC2 temporary deployment

Status on 2026-09-28: **PARTIAL**. The controller endpoint and its local and
external unauthorized authentication gates passed. Physical PTT acceptance,
real APNs delivery, and a positive credentialed login from an outside runner
remain unverified. `READY_FOR_PHYSICAL_QA=no`.

## Source and service

- Installed controller source and systemd unit match pushed commit
  `efb852a001c604c97d31cca5df5da3bee0bfb8a3` byte for byte.
  Subsequent repository commits add only deployment tests, checks, workflow,
  and documentation; no controller source was redeployed.
- `slime-talk-feasibility.service` is active after a scoped restart at
  2026-09-28 17:07:32 UTC, with `NRestarts=0` and only
  `127.0.0.1:8787` listening for the controller. The restart cleared the
  in-memory test sessions; the LiveKit participant check found zero clients.
- Root gate: `sudo /usr/bin/python3 deploy/nuc2_root_gate.py` passed its
  permission, installed-byte, service, participant, and secret-log checks.
  The first gate run reached the participant query after a successful restart
  but failed because the check did not accept LiveKit's closed-room HTTP 404.
  The corrected gate passed on the second run; both restarts had zero service
  restarts and a loopback listener.
- `/etc/slime-talk-feasibility` is `root:slime-talk 0750`;
  `controller.env` is `root:root 0600`; `apns.p8` and `devices.json` are
  `root:slime-talk 0640`. The dedicated service account is `slime-talk`.
  No private file or value is committed.

## Local gates

- `cd controller && npm test`: 12 passed, 0 failed.
- `python3 ci/security_check.py`: PASS; `git diff --check`: PASS.
- `deploy/smoke_controller.py` under isolated `livekit==1.1.19`: invalid
  pairing and absent session rejected; both real device logins passed; two
  receive-only LiveKit clients connected; single-owner arbitration, busy
  denial, renewal, release, stale-epoch rejection, and lease expiry passed.
  The script publishes no tracks and registers no APNs token.
- Both clients explicitly disconnected, then Python collected SDK handles
  before interpreter exit. Exit code 0, no `FfiHandle`/`AssertionError` or
  other traceback. The earlier shutdown assertion was a test-client teardown
  issue; no controller failure was observed. This is a scoped SDK cleanup
  finding, not a claim that every SDK lifecycle is proven.
- Local unauthenticated `/status` and invalid `/login` returned HTTP 401 with
  only `{"error":401}`. Journal checks found no known pairing/LiveKit/APNs
  credentials, JWT pattern, or private-key marker. These are targeted audits,
  not a guarantee against every possible leak.

## Public endpoint and rollback

- Installed Tailscale 1.102.2 help and current configuration were inspected
  before activation. The authorized HTTPS Funnel mapping is
  `https://slimy-nuc2.tailf64507.ts.net:8443` to
  `http://127.0.0.1:8787`.
- The unrelated HTTPS 443 mapping to `http://127.0.0.1:8080` was verified
  before activation, after activation, during scoped rollback, and after
  restoration. It was never reset or changed. No SSH, public controller bind,
  or broad firewall change was made.
- A NUC2-originated HTTPS request returned 401 with successful TLS
  verification; this is explicitly a local-path check.
- Independent GitHub-hosted runner [run 36456018510](https://github.com/GurthBro0ks/slime_talk/actions/runs/36456018510)
  returned verified-TLS HTTP 401 for unauthenticated `/status` and invalid
  `/login`. After rollback and restoration, independent
  [run 36456104367](https://github.com/GurthBro0ks/slime_talk/actions/runs/36456104367)
  passed the same checks. No pairing key was sent to that runner.
- Scoped rollback command `tailscale funnel --https=8443 off` removed only
  8443. The installed CLI then showed only the intact 443 mapping. Restoring
  only `tailscale funnel --bg --https=8443 http://127.0.0.1:8787`
  restored the exact authorized mapping. Final Funnel ports: 443 and 8443.
  The service remains enabled and running for the temporary test window.

## Enrollment and remaining gates

- Existing distinct Pixel and iPhone pairing keys remain private. The
  `deploy/show_device_pairing.py` helper shows only the selected key in the
  owner's private interactive terminal for later device enrollment. The
  Android and iOS clients store pairing material with platform protected
  storage. No new keys were generated during this deployment continuation.
- A positive credentialed login from outside NUC2 was not run: the public
  runner received no private pairing credentials. Local real-device
  credential checks and external credential rejection both passed.
- Deliberate APNs delivery was not attempted. No dummy token remains from
  the earlier test after the service restarts; physical iPhone push behavior
  still requires a genuine device token and separate physical QA.
- Pixel/iPhone live audio, locked iPhone wake and transmission, receive-only
  first playback, capture shutdown, simultaneous presses, and silence timeout
  remain unverified on physical devices. TestFlight build 0.1.0 (16) was left
  unchanged; its processing investigation is separate.

Rollback if the temporary endpoint must be closed: run
`tailscale funnel --https=8443 off`, then stop/disable only
`slime-talk-feasibility.service` as appropriate. Preserve port 443.
