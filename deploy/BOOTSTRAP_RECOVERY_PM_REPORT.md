# Canonical PM report — bootstrap recovery 001

Final closeout: 2026-09-28, after CI completed at 19:34:06 UTC. Apple distribution is BLOCKED because no installable build was established within the existing bounded poll. Transport acceptance is confirmed; Apple upload/processing failure is not established.

```text
PHASE=PHASE_0_FEASIBILITY
WORK_ORDER=SLIME_TALK_BOOTSTRAP_RECOVERY_001
RESULT=BLOCKED
APPLE_DISTRIBUTION=BLOCKED

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
BUILD_17_SIGNING=PASS; automatic archive and exported signatures valid; exact app/team matches; current profiles
BUILD_17_ENTITLEMENTS=PASS; archive/export PushToTalk present; exported production APNs; non-debug App Store profile
UPLOAD_TRANSPORT_RESULT=accepted; single upload step succeeded
UPLOAD_REQUEST_ID=not_returned; CI extractor result; see limitation below
UPLOAD_RECORD_ID=unavailable; upload-record endpoint not queried in this run
UPLOAD_RECORD_STATE=unknown; no upload record retrieved
UPLOAD_TIMESTAMP_UTC=2026-09-28T19:14:57.639578+00:00; runner timestamp immediately after command return
IOS_VERSION=0.1.0
IOS_BUILD=17
IPA_SHA256=b6006d3ed50c2ade68b59cd224be1a884a963e281a8b8b27ebfe774ae85d65be
BUILD_17_FOUND=no; 20 successful complete filtered responses
BUILD_RESOURCE_ID=none
BUILD_PROCESSING_STATE=unknown
TESTFLIGHT_VISIBILITY=no; authenticated UI reconfirmed No Builds after poll
INTERNAL_TESTFLIGHT_AVAILABILITY=not established; no installable build
APPLE_API_AUTHORIZATION_ERRORS=none reported in build17 poll
EXPLICIT_APPLE_PROCESSING_FAILURE=not observed

IPHONE_INSTALL=not started; no usable internal TestFlight build established
IPHONE_ENROLLMENT=not started
IPHONE_RECEIVE_ONLY_CONNECTIVITY=not tested
IPHONE_MIC_ACTIVATED_DURING_BOOTSTRAP=not tested; bootstrap not performed

PAIRING_SECRET_EXPOSURE=no observed
SECRETS_AUDIT=PASS scoped tracked-source and controller known-secret scans; not a comprehensive historical audit
BLOCKERS=no installable build17 after bounded poll; upload record/state unavailable; direct Pixel session identity and per-request status proof unavailable
RISKS=earlier Pixel connection loss; subsequent stable reconnect; session attribution is timing correlation; stored credential not independently inspected on device
READY_FOR_PHYSICAL_QA=no
RECOMMENDED_NEXT=PM/owner review unsubmitted Apple escalation draft; no further upload or extended polling
```

## Verified evidence

- Exactly one new build-17 workflow dispatched: https://github.com/GurthBro0ks/slime_talk/actions/runs/36469738250 . Workflow commit `4aeb9473b859b88c5f2f5a3ab99aa960a83696da`. Owner approved the existing protected signing environment. Compile and signed-candidate/upload steps succeeded. The existing bounded poll performed 20 queries from 19:14:58.794Z through 19:34:02.049Z; all reported BUILD_17_FOUND=no. The run completed at 19:34:06Z with CI conclusion failure because its availability gate was not met. This is not an explicit Apple rejection. Cleanup passed. No new upload, workflow rerun, or extended Apple polling occurred.
- Frozen runtime byte comparison, Swift safety checks, controller tests (12/12), source credential checks, and unsigned compilation passed. Signing/upload step enforces automatic archive signatures, archive app/profile PushToTalk, exact identifiers, current profiles, exported PushToTalk and production APNs, valid exported signatures, non-debug App Store profile, exact 0.1.0/build 17, and IPA hashing before its single upload. Production APNs and App Store profile requirements apply to exported distribution output; the proven automatic archive path may use a development profile.
- Completed CI logs confirm transport acceptance and the timestamp/digest above. UPLOAD_REQUEST_ID=not_returned is the allowlisted extractor output, not proof that the original raw response contained no other delivery/upload identifier: the extractor recognized selected request-ID/UUID fields, and raw output was deleted during private cleanup. No request, delivery or upload ID can be recovered from the retained evidence. The timestamp is the runner observation immediately after the upload command returned, not an Apple server-receipt timestamp. Raw responses and credentials are not included.
- Owner authorized private USB autofill as an amendment to manual typing. The agent never executed the private helper or read the pairing key. USB was used only for field entry and safe observations, never as a network proxy, VPN or reverse tunnel. Actual Pixel hotspot Wi-Fi and NOT_VPN state were observed; Tailscale was force-stopped and confirmed absent. iPhone cellular upstream was owner-confirmed.
- Pixel initially connected, lost controller/media connectivity, then reconnected successfully at epoch-ms `1790622821750`. Subsequent inspected trace showed no new connection-loss, PTT press, hardware-capture-start, or publication-ready event.
- Owner read-only LiveKit observation at epoch seconds `1790622975` found one UUID participant, digest `5c0505f06195ef86`, unchanged from the previous observation. Corrected observer verified subscribe=true, publish=false, publish_data=false, zero tracks and controller known-secret scan PASS. An initial false subscribe result was an observer casing bug, corrected for LiveKit snake_case fields; no runtime permissions were changed.
- The participant is correlated with the isolated Pixel join by timing; the current app/controller do not directly expose the issued phone session identity. Sustained connection supports successful status polling but is not an independent HTTP-response capture. These limitations prevent claiming every strict positive-auth acceptance criterion fully closed.

## Scope and decision

No runtime/product changes, production implementation, PTT presses, audio publication, or F1–F7 acceptance were performed. No build 18 is authorized or attempted. iPhone preparation remains conditional on a usable internal build 17. No owner/legal attestation was answered. The authenticated TestFlight page showed No Builds; no specific attestation question was presented in that view.

The distribution repeat-failure rule now applies: APPLE_DISTRIBUTION=BLOCKED and READY_FOR_PHYSICAL_QA=no. This is an operational readiness conclusion, not a claim that Apple explicitly rejected the upload. iPhone preparation cannot proceed. Review `deploy/APPLE_DISTRIBUTION_ESCALATION_DRAFT.md`; it has not been submitted.

## Apple evidence interpretation

| Evidence | Final result | Meaning |
|---|---|---|
| Upload command | accepted | Transport command succeeded; does not prove ingestion/processing success. |
| Build API | 20 successful complete filtered responses; no match | No version 0.1.0/build 17 resource found during the bounded window. |
| API authorization | No HTTP errors emitted in build17 run | The missing-build result is not an authorization failure. Earlier build16 upload-endpoint 403s are separate historical evidence. |
| Upload resource | Not queried/retrieved in this run | ID and processing state unavailable; cannot classify it as failed, processing, or absent. |
| Explicit processing state | unknown | No PROCESSING, FAILED or INVALID build state was returned. |
| TestFlight UI | Authenticated No Builds after poll | No visible/installable internal build established; not proof of failed upload. |
| CI conclusion | failure | The scripted distribution-availability criterion was unmet; Apple did not return an explicit rejection in retained evidence. |

Sanitized machine-readable evidence: `deploy/BUILD17_SAFE_CI_EVIDENCE.json`. All recorded poll timestamps and safe signing/upload labels are retained there. The poll checks the app ID and bundle ID, exact build number plus included pre-release version, and rejects paginated/incomplete lists before emitting a result. No additional Apple API request was made during closeout.
