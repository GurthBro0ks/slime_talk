# slime_talk — experimental feasibility only

Phase 0, Gate 0C. Active work order: SLIME_TALK_FEASIBILITY_002,
continuing the scope and F1–F7 tests of SLIME_TALK_FEASIBILITY_001.
Production implementation and architecture freeze are not authorized.

## Proven build prerequisite — 2026-09-26

[Hosted preflight run 1](https://github.com/GurthBro0ks/slime_talk/actions/runs/36248232389)
passed at commit `8001a8f6c68b4ab0574176b770b2d6e36eb6aa81`.

- Standard GitHub-hosted `macos-15` runner, image `macos-15-arm64/20260907.0337.1`.
- macOS 15.7.9 (24G830), arm64.
- Xcode 26.3 (17C529), Swift 6.2.4, iOS SDK 26.2.
- Swift type-check of public PushToTalk and AVFoundation framework types against the iPhoneOS SDK: PASS.
- This is a compiler/toolchain check, not a simulator or physical-device result.
- No app was built, signed, installed, or uploaded to TestFlight.

The workflow has no checkout, dependencies, credentials, artifact uploads, or cache actions.
It runs manually, or when its own workflow file changes on main.
It skips its job if the repository is private; revisit cost authorization before changing that guard.
Standard hosted runners in public repositories are free under
[GitHub's documented billing rules](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

## Preflight status — 2026-09-26

- Apple Developer membership and portal access verified.
- Explicit feasibility App ID `ai.slimy.slimetalk.feasibility` registered under owner authorization.
- Push to Talk and Push Notifications are enabled in the saved App ID.
- No separate capability approval was requested during ordinary registration.
- One APNs key registered with only APNs service enabled, Production environment,
  and a topic restriction to the feasibility App ID.
- Owner downloaded the APNs key and saved repository secret `APNS_AUTH_KEY_P8`.
- GitHub confirms the secret exists. Its value is not readable through the settings UI.
- Non-disclosing format validation FAILED: the stored value did not contain exactly
  one complete expected `PRIVATE KEY` PEM block. The credential was not printed or modified.
- App Store Connect requires acceptance of its Terms of Service before further setup.
  The agreement has not been accepted by Engineering.
- Signing identity, signed profile entitlements, App Store Connect app/upload access,
  TestFlight install, LiveKit development project, controller endpoint, and physical
  device test coordination remain unresolved.

The owner authorized only the minimum feasibility App ID/capabilities, signing,
provisioning, APNs, free LiveKit project, hosted signed builds, and TestFlight path.
No purchases, paid infrastructure, unrelated capabilities, or production build are authorized.

### Immediate setup blockers

1. The owner must review the App Store Connect Terms of Service. No agreement has
   been accepted on the owner's behalf, and signing/TestFlight setup is paused.
2. The owner must replace `APNS_AUTH_KEY_P8` with the original Apple-downloaded P8
   text, including the BEGIN/END PRIVATE KEY lines and real line breaks. Do not
   paste credentials into chat. Retain a secure backup.

[APNs credential validation run 2](https://github.com/GurthBro0ks/slime_talk/actions/runs/36253714786)
at commit `8ad83dce14cadacd442020859e0b97b19f0d3d92`:

- Six synthetic parser/signing checks: PASS.
- Real stored secret: FAIL before cryptographic parsing; expected one complete PEM block.
- No network calls with the key, repository checkout, dependencies, caches, or artifact uploads.
- Validator uses fixed result messages; temporary source and executable removed.
- GitHub masked the secret environment value in logs.
- This check does not prove the private key matches the registered Apple key ID or
  that APNs will authorize a push.

Workflow: `.github/workflows/apns-credential-check.yml`. After correcting the secret,
run **APNs credential format check** manually on `main`. The full original P8 text is
the expected format; trimming the PEM boundary lines is incorrect. Runtime credentials
must not be made available to unrelated build steps.

Key registration and portal capability checks do not prove APNs delivery or signed
entitlements. The production `.voip-ptt` push must still be tested with a real
PushToTalk channel token from the TestFlight candidate.

## Frozen PTT behavior

One private room and one authoritative transmitter. Backend authorization must precede
capture/publication. Stop on release, touch cancellation, authorization loss,
connection failure, invalid session, or three seconds without qualifying local speech.
Silence timeout stops capture and publication and releases ownership. Continued hold
must not reacquire ownership; release plus a fresh press is required. There is no
arbitrary maximum talk-duration cap.

## Physical-device gate

All required tests are NOT TESTED:

- F1: understandable live speech in both directions, Pixel 6 Pro and iPhone 16 Pro.
- F2: genuinely locked/suspended iPhone receives using Apple PTT wake; measure onset loss and wake latency.
- F3: genuine locked system PTT transmission; system activation is not backend authorization.
- F4: first receive-only playback with microphone never activated; instrument session, engine, subscription, first PCM.
- F5: actual capture/publication shutdown for every required stop condition.
- F6: simultaneous presses grant exactly one transmitter; loser sends no audio.
- F7: three-second silence releases ownership and requires release plus fresh press.

[LiveKit Swift issue 1069](https://github.com/livekit/client-sdk-swift/issues/1069)
was open at inspection. It is a reported receive-only integration issue, not proof
that this candidate will fail. Activating the microphone first is not an acceptable workaround.

## Evidence boundaries

Never infer latency or microphone shutdown from UI state alone. Do not record speech
content or publish credentials, private-device identifiers, APNs device tokens, or
personal account information in this public repository or its logs. Store only
redacted evidence. Application-level E2EE is outside the approved feasibility scope.

Overall feasibility result: BLOCKED pending setup; architecture remains unproven.
