# Canonical PM report — bootstrap recovery 001

As of 2026-09-28 19:23 UTC. Final handoff for this reporting point; the already-running bounded Apple poll has not finished. No terminal Apple processing outcome is asserted.

```text
PHASE=PHASE_0_FEASIBILITY
WORK_ORDER=SLIME_TALK_BOOTSTRAP_RECOVERY_001
RESULT=PARTIAL

PIXEL_APK_VERSION=0.1.0
PIXEL_APK_BUILD=4
PIXEL_INSTALL=verified; physical Pixel 6 Pro
PIXEL_TRANSPORT=wifi_to_iphone_hotspot
UPSTREAM_INTERNET=iphone_cellular; owner-confirmed setup
PIXEL_NATIVE_CELLULAR=NOT_TESTED
PIXEL_ENROLLMENT=accepted; Keystore AES-GCM storage path verified in source
PIXEL_PUBLIC_AUTH=successful login inferred from real app media_connected
PIXEL_STATUS=successful polling supported by sustained connection; individual HTTP responses not directly captured
PIXEL_LIVEKIT_RECEIVE_ONLY=PASS; subscribe=true, publish=false, publish_data=false
PIXEL_MIC_ACTIVATED=no observed activation
PIXEL_AUDIO_PUBLISHED=no; server observed zero published tracks

BUILD_16_DISPOSITION=transport accepted; no server build resource found; TestFlight not visible; processing unknown; unusable; not retried
BUILD_17_SOURCE=c16987116823f5f96fd7e09e2f0b02efc2c20dfc
BUILD_17_SIGNING=PASS verification step; detailed labels pending completed CI log
BUILD_17_ENTITLEMENTS=PASS verification step; detailed labels pending completed CI log
UPLOAD_TRANSPORT_RESULT=accepted; single upload step succeeded
UPLOAD_REQUEST_ID=pending completed CI log; not yet known whether Apple returned one
UPLOAD_TIMESTAMP_UTC=pending exact evidence; upload step completed 2026-09-28T19:14:57Z
IOS_VERSION=0.1.0
IOS_BUILD=17
IPA_SHA256=pending completed CI log
BUILD_17_FOUND=poll in progress; final API result not yet available
BUILD_RESOURCE_ID=not yet established
BUILD_PROCESSING_STATE=unknown
TESTFLIGHT_VISIBILITY=no; authenticated UI showed No Builds

IPHONE_INSTALL=not started; no usable internal TestFlight build established
IPHONE_ENROLLMENT=not started
IPHONE_RECEIVE_ONLY_CONNECTIVITY=not tested
IPHONE_MIC_ACTIVATED_DURING_BOOTSTRAP=not tested; bootstrap not performed

PAIRING_SECRET_EXPOSURE=no observed
SECRETS_AUDIT=PASS scoped tracked-source and controller known-secret scans; not a comprehensive historical audit
BLOCKERS=usable build17 not established; bounded Apple poll unfinished; direct Pixel session identity and per-request status proof unavailable
RISKS=earlier Pixel connection loss; subsequent stable reconnect; session attribution is timing correlation; stored credential not independently inspected on device
READY_FOR_PHYSICAL_QA=no
RECOMMENDED_NEXT=collect completed build17 poll and safe upload metadata; no additional upload; if no usable build appears, mark Apple distribution BLOCKED and escalate to Apple Developer Support / Feedback Assistant
```

## Verified evidence

- Exactly one new build-17 workflow dispatched: https://github.com/GurthBro0ks/slime_talk/actions/runs/36469738250 . Workflow commit `4aeb9473b859b88c5f2f5a3ab99aa960a83696da`. Owner approved the existing protected signing environment. Compile and signed-candidate/upload steps succeeded; post-upload API polling remains in progress at this cutoff. Its bounded window began 19:14:57 UTC and ends approximately 19:35 UTC.
- Frozen runtime byte comparison, Swift safety checks, controller tests (12/12), source credential checks, and unsigned compilation passed. Signing/upload step enforces automatic archive signatures, archive app/profile PushToTalk, exact identifiers, current profiles, exported PushToTalk and production APNs, valid exported signatures, non-debug App Store profile, exact 0.1.0/build 17, and IPA hashing before its single upload. Production APNs and App Store profile requirements apply to exported distribution output; the proven automatic archive path may use a development profile.
- Raw Apple upload response was kept private by CI. Request ID, timestamp and IPA digest are emitted through restricted evidence handling, but completed CI logs were not yet available at report time. No request ID is invented, and no transport success is equated with TestFlight success.
- Owner authorized private USB autofill as an amendment to manual typing. The agent never executed the private helper or read the pairing key. USB was used only for field entry and safe observations, never as a network proxy, VPN or reverse tunnel. Actual Pixel hotspot Wi-Fi and NOT_VPN state were observed; Tailscale was force-stopped and confirmed absent. iPhone cellular upstream was owner-confirmed.
- Pixel initially connected, lost controller/media connectivity, then reconnected successfully at epoch-ms `1790622821750`. Subsequent inspected trace showed no new connection-loss, PTT press, hardware-capture-start, or publication-ready event.
- Owner read-only LiveKit observation at epoch seconds `1790622975` found one UUID participant, digest `5c0505f06195ef86`, unchanged from the previous observation. Corrected observer verified subscribe=true, publish=false, publish_data=false, zero tracks and controller known-secret scan PASS. An initial false subscribe result was an observer casing bug, corrected for LiveKit snake_case fields; no runtime permissions were changed.
- The participant is correlated with the isolated Pixel join by timing; the current app/controller do not directly expose the issued phone session identity. Sustained connection supports successful status polling but is not an independent HTTP-response capture. These limitations prevent claiming every strict positive-auth acceptance criterion fully closed.

## Scope and decision

No runtime/product changes, production implementation, PTT presses, audio publication, or F1–F7 acceptance were performed. No build 18 is authorized or attempted. iPhone preparation remains conditional on a usable internal build 17. No owner/legal attestation was answered. The authenticated TestFlight page showed No Builds; no specific attestation question was presented in that view.

PM should retain RESULT=PARTIAL and READY_FOR_PHYSICAL_QA=no at this cutoff. If the bounded poll finishes without a usable build, apply the work order's repeat-failure rule: Apple distribution BLOCKED, preserve safe upload evidence, recommend Apple support escalation, and do not retry or change architecture. If a build is still explicitly processing, record that exact state. If usable, proceed only with authorized iPhone install/enrollment/receive-only checks.
