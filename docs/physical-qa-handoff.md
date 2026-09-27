# Physical feasibility handoff — SLIME_TALK_FEASIBILITY_003

Engineering preparation only. Independent QA owns acceptance. All F1–F7 are
NOT TESTED on physical devices as of 2026-09-27.

## Before installation

1. Complete protected iOS run 16; require same-candidate entitlement/profile PASS,
   upload acceptance, and App Store Connect processing before assigning internal testing.
   Stop on any export-compliance/legal question and relay its exact text to the owner.
2. Identify the owner NUC, provision private runtime files per deploy/README.md,
   and obtain Canonical-relayed approval before enabling public Funnel.
3. Validate controller/API/media/APNs operation without logging credentials.
4. Record phone OS versions, app versions/builds, source commits, network type,
   controller commit and clock synchronization. Keep device identifiers private.

## Android installation

In GitHub Actions run 36334126880, download artifact
`slime-talk-feasibility-apk`, unzip it, and install `app-debug.apk` on the Pixel.
Version 0.1.0 / versionCode 4. Source:
`d6cfe4c8cdb0dc5b5137506dc9889d767e2d8518`.
APK SHA-256 (not the ZIP):
`7a3d3b9b6a2e6f836fec73e7584ff178a824dcf26add76ca5fd99a151dbce065`.

Use Android's explicit per-source installation permission if prompted. This is a
debug feasibility APK, not Play Store distribution. A later hosted debug build may
use another signing certificate; do not erase an installed app silently to replace it.
Artifact retention is seven days.

## iPhone installation

No TestFlight build is available yet. Once processing succeeds, the owner installs
the actual runtime candidate through the authorized internal TestFlight app entry.
Record the displayed version/build. Do not install or test the static signing probe.

## Enrollment and evidence

Both apps have a one-time HTTPS controller origin and private per-device key form.
Use only that phone's key; never enter LiveKit/APNs/server secrets. Join/reconnect
explicitly and grant microphone permission. Permissions alone are not proof of capture.
The iPhone must join the genuine Apple PTT channel before locked tests.

Use the iPhone Share QA trace and Android Copy QA trace controls after each case.
Controller logs contain event/epoch/timing metadata. Keep evidence private until
reviewed; do not publish enrollment credentials, APNs tokens, JWTs or voice content.
Clocks on different machines are not directly interchangeable: calculate intervals
on one monotonic clock where possible, record clock offsets for cross-device measures.

## Required physical cases

- F1: understandable live speech both directions.
- F2: properly joined, locked/suspended iPhone receives Pixel speech via genuine
  Apple PTT wake; measure readiness and beginning-of-speech loss. No keep-awake trick.
- F3: genuine locked system control; backend grant and Apple readiness precede
  capture/publication. A system cue is not a grant.
- F4: fresh joined iPhone with mic never activated; inspect subscription, engine,
  Apple activation and first remote PCM. Stop if mic-first activation is necessary.
- F5: release, silence expiry, authorization loss and connection loss; correlate
  actual capture callbacks/engine state, publication stop and receiver observations.
  UI state alone is insufficient.
- F6: near-simultaneous requests; one epoch owner and no losing-phone audio.
- F7: speech then at least three seconds silence while held; capture/publication off,
  ownership released, continued hold never restarts. Release and fresh press succeeds.
  Pay particular attention to Apple system callbacks following forced termination.

Test both Wi-Fi and cellular as the authorized QA protocol requires. Mark untested
conditions NOT TESTED. Do not infer acceptance from automated tests or installation.

## Reproducible automated checks

```sh
node --test controller/test/*.mjs
python3 ci/security_check.py
python3 ci/test_signing_diagnostics.py
bash android/gradlew -p android testDebugUnitTest assembleDebug --no-daemon
# macOS with Swift:
swiftc ios/SlimeTalk/PTTCore.swift ci/test_ptt.swift -o /tmp/slime-ptt-tests
/tmp/slime-ptt-tests
```

The iOS workflow supplies Xcode and compiles the full native candidate; protected
manual execution signs, verifies and optionally uploads only that verified runtime.
No public endpoint is authorized by these instructions.
