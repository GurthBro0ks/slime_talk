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

## Remaining preflight

- Apple Developer membership and portal access verified.
- Push to Talk and Push Notifications selectable in the App ID registration form.
- Proposed explicit Bundle ID: `ai.slimy.slimetalk.feasibility`.
- App ID draft reached confirmation; registration not submitted.
- APNs key inventory and provisioning-profile inventory empty at inspection.
- Signing identity, signed profile entitlements, App Store Connect app/upload access,
  TestFlight install, LiveKit development project, controller endpoint, and physical
  device test coordination remain unresolved.

No Apple account settings may be changed without the owner's authorization.

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
