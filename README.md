# slime_talk — experimental feasibility only

Phase 0, Gate 0C. Active work order: SLIME_TALK_SIGNING_DIAGNOSTIC_001.
Focused signing/provisioning diagnosis and minimal local repair only. The physical
feasibility requirements of SLIME_TALK_FEASIBILITY_001 remain unchanged.
Production implementation and architecture freeze are not authorized.

## Signing diagnostic — original failure isolated, repair experiment prepared — 2026-09-27

Active scope: SLIME_TALK_SIGNING_DIAGNOSTIC_001. No app implementation or
architecture changes are authorized by this diagnostic order.

[Protected diagnostic run 5](https://github.com/GurthBro0ks/slime_talk/actions/runs/36320129005),
commit `8bfaae911798675762c34410ff6ca19e9001b354`, completed after owner approval.
Native compilation and cleanup passed. Distribution export produced a valid
signature, but the precise verifier correctly rejected missing app entitlements:

```text
SIGNED_APP_PTT_ENTITLEMENT=missing
PROFILE_PTT_ENTITLEMENT=present
SIGNED_APP_APNS=missing
PROFILE_APNS=production
SIGNED_APP_APP_ID=match
PROFILE_APP_ID=match
SIGNED_APP_TEAM=match
PROFILE_TEAM=match
PROFILE_TEAM_METADATA=match
SIGNED_APP_NON_DEBUG=yes
PROFILE_NON_DEBUG=yes
PROFILE_TYPE=app-store
PROFILE_EXPIRY=current
SIGNATURE=valid
BUNDLE_ID=match
PTT_BACKGROUND_MODE=present
```

**ORIGINAL_FAILURE_COMPONENT=signed_app.** Apple provisioning permits both required
capabilities on this candidate. The old check was not a false positive; its error
message was insufficiently specific. Why unsigned archive/export omitted the app
entitlements remains an unproven build-path hypothesis until signed archiving runs.

The diagnostic log inspection found no raw private-key block, unexpected long
base64 line, or JWT value. Cleanup succeeded; no artifacts or TestFlight build were
uploaded. This limited log inspection is not a comprehensive account security audit.

### Prepared standard signed-archive experiment

Workflow implementation commit `7cd594a70683962fb3946cbfd8b79d190790416c`;
cleanup refinement `d9686413957a4c23c5432b2baeef3710cdf72435`, corrected before
signing at `5d8a5dbf28e9bc3d0b809285445c24d0018e31a9`.

- Existing bundle/team/capabilities and existing protected API key only.
- Archive with `CODE_SIGNING_ALLOWED=YES`, `CODE_SIGN_STYLE=Automatic`,
  `-allowProvisioningUpdates`, and the existing authentication-key arguments.
- Temporary local runner keychain; original default/search list restored.
  Newly downloaded runner profiles and private temporary files are cleaned up.
  No Apple certificate/key deletion or capability toggling.
- Inspect signed archive app/profile PTT, APNs, identifiers, expiry and signature
  before distribution export. Export retains the strict app/profile acceptance
  checks. Missing app `get-task-allow` is not accepted as implicit false.
- Raw signing logs stay private. No artifact or TestFlight upload step.
- Pushes only run non-secret checks/compilation. Signing still requires a manual
  workflow dispatch and the existing `ios-feasibility-signing` owner review.
- Offline test command: `python3 ci/test_signing_diagnostics.py`.
  Sixteen synthetic diagnostic/security cases and embedded Python syntax are
  checked before compilation, without credentials.
- [First preparation check](https://github.com/GurthBro0ks/slime_talk/actions/runs/36325149877)
  passed. This is NOT evidence that signed archiving works.
- [Cleanup-refinement check](https://github.com/GurthBro0ks/slime_talk/actions/runs/36325188784)
  caught an indentation error before compilation or credential access.
- [Corrected preparation check](https://github.com/GurthBro0ks/slime_talk/actions/runs/36325275292)
  passed syntax, all 16 regression checks, native compilation, and cleanup.
  Signing remains manual and protected.

The signed-archive experiment has not been dispatched. The current assistant
execution environment failed and browser control is unavailable; the available
GitHub connector can inspect/update the repository but cannot dispatch a workflow.
Owner continuation: Actions → iOS signing and entitlement probe → Run workflow →
main, then approve the protected environment review. Do not rerun diagnostic run 5,
which would use the old unsigned-archive path.

No Apple capability/profile repair is indicated by run 5. All physical tests remain
NOT TESTED. No TestFlight readiness or architecture acceptance is claimed.

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
- No separate PushToTalk capability approval was requested during ordinary registration.
- One APNs key registered with only APNs service enabled, Production environment,
  and a topic restriction to the feasibility App ID.
- Owner saved and corrected repository secret `APNS_AUTH_KEY_P8`.
- Stored credential format and local signing check: PASS; no wrapper text remains.
- Owner accepted App Store Connect Terms of Service; authenticated Apps access verified.
- Created iOS-only App Store Connect record **slime talk Feasibility**:
  Apple app ID `6816454718`, bundle `ai.slimy.slimetalk.feasibility`,
  SKU `slime-talk-feasibility-001`, primary language English (U.S.).
- No build has been uploaded and no app has been submitted for public distribution.
- The hosted export created an Apple Distribution Managed certificate (portal verified,
  expiry 2027-09-26). Export and application signature integrity checks completed,
  but required PushToTalk entitlement verification failed. Provisioning is NOT accepted.
- Owner completed the App Store Connect API access request; access is approved.
- Owner explicitly approved an account-wide Admin team API key for CI.
- Created the named key `slime talk Feasibility CI` and stored its complete private-key PEM
  as `ASC_API_KEY_P8` in the protected GitHub environment. GitHub storage was verified.
- The owner downloaded the P8 in the cloud browser; Engineering transferred it directly
  from the shared download into the secret field without displaying the value.
  Local OpenSSL parsing passed; the temporary downloaded file was then removed.
- LiveKit project `slime-talk-feasibility` is created on the free Build plan,
  United States region; next invoice displayed $0.00. Agent observability is disabled.
- LiveKit project credentials are stored as GitHub Actions secrets and the read-only
  API access check passed. No media room, agent, recording, or paid resource was created.

The owner authorized only the minimum feasibility App ID/capabilities, signing,
provisioning, APNs, free LiveKit project, hosted signed builds, and TestFlight path.
No purchases, paid infrastructure, unrelated capabilities, or production build are authorized.

### Current setup blockers

1. **STOP CONDITION:** run `36257775576` was approved by the owner and failed the
   required PushToTalk entitlement check after producing an exported signed app.
   No signing retry, capability change, or provisioning workaround has been made.
2. The current fixed diagnostic does not distinguish the app-signature entitlement
   from the embedded-profile entitlement. The unsigned-archive-to-distribution export
   path may have dropped the requested entitlement; this is an unproven hypothesis,
   not evidence that Apple's PushToTalk provisioning is unavailable.
3. Controller hosting endpoint/access and physical-device test coordination remain
   unresolved. A signing-only iOS probe exists; PTT clients and controller are not implemented.

### APNs secret validation

[APNs credential validation run 3](https://github.com/GurthBro0ks/slime_talk/actions/runs/36254114573)
at commit `79eaf47ba69ca4a38277c9d5f7669bdda4765e1a` passed after the owner corrected
the saved secret:

- Six synthetic parser/signing checks: PASS.
- OpenSSL P-256 PEM parsing: PASS.
- Apple CryptoKit private-key import and local sign/verify: PASS.
- No extra wrapper text; only line-ending/outer-whitespace normalization.
- Secret environment value masked in logs; no unexpected raw base64 output detected.
- No key-bearing network calls, repository checkout, dependencies, caches, or artifact uploads.
- Temporary validator source and executable removed.

Earlier runs failed at PEM boundary validation and are retained as historical evidence.
No key value was printed or modified by Engineering. The complete original P8 text,
including its BEGIN/END PRIVATE KEY lines, is the correct stored format.

Workflow: `.github/workflows/apns-credential-check.yml`. Reproduce with
**Actions → APNs credential format check → Run workflow → main**.

These checks do NOT prove key identity, APNs authorization/delivery, or signed app
entitlements. A production `.voip-ptt` push still needs a real PushToTalk channel
token from the TestFlight candidate. Runtime credentials must not be supplied to
unrelated build steps.

### Protected CI credential destination

GitHub environment `ios-feasibility-signing` is configured with:

- Required reviewer: repository owner `GurthBro0ks`.
- Only the `main` branch is allowed; no tags.
- Administrator bypass disabled.
- Self-review prevention remains off so the sole owner can approve their own triggered build.
- Non-secret environment variables saved: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `APPLE_TEAM_ID`.
- Environment secret `ASC_API_KEY_P8` is stored. Its value was not printed, committed,
  or added to any report, screenshot, or artifact.

Any future signing job must explicitly use this environment. These protections do not
apply to the existing APNs/LiveKit repository secrets, which are exposed only to their
dedicated validation steps. Credential values must never enter application source,
checkout-dependent scripts, logs, caches, or downloadable artifacts.

Apple documents team-wide key scope in
[App Store Connect API help](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-api/).
The automatic signing path remains an experiment. It produced a managed distribution
certificate and an exported signed app, but the required PushToTalk entitlement check
failed. Successful signing alone does not satisfy the provisioning or physical-device gates.

### Apple CI credential validation — PASS

Workflow: `.github/workflows/asc-credential-check.yml`, commit
`960c08f4d9fc88a36814b568c287825ee8f28cc5`.

- Manual only, public repository and `main` guards, `ios-feasibility-signing` environment.
- No repository checkout, dependencies, caches, artifacts, or private-key file writes.
- Imports the full P8 PEM in memory, checks P-256, and verifies a local ES256 signature.
- A 120-second JWT is restricted to two GET requests for the exact feasibility
  App Store Connect app and registered App ID; response bodies and credentials are not logged.
- No signing/provisioning/account mutations.
- Local YAML parsing and embedded JavaScript syntax checks: PASS.
- Downloaded source-key OpenSSL parsing: PASS.
- [Run 1](https://github.com/GurthBro0ks/slime_talk/actions/runs/36256889270) passed after owner review
  at commit `26157d76e6e861c45c4724d0b73bc0da305dd595`.
- Stored P-256 private-key import and ES256 sign/verify: PASS.
- Read access to the exact feasibility App Store Connect app and registered App ID: PASS.
- Secret was masked in Actions logs; no unexpected raw base64 line detected.

Reproduce with **Actions → Apple CI credential check → Run workflow → main**,
then review and approve the protected environment job.
This validation does not prove cloud signing or provisioned PushToTalk entitlements.

### LiveKit credential validation

[LiveKit credential validation run 1](https://github.com/GurthBro0ks/slime_talk/actions/runs/36254826920)
passed at commit `024bdc1cd53e6a86cbd57fad77102b3277f5998f`.

- Stored `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` authenticated
  a read-only `RoomService/ListRooms` request: PASS.
- JWT limited to `roomList`, valid for 60 seconds; response data and credential values not logged.
- API key and secret masked in job logs; no unexpected raw base64 line detected.
- No checkout, third-party dependencies, artifacts, caches, or resource creation.
- Media transport, controller authorization, and F1–F7 remain NOT TESTED.

Reproduce with **Actions → LiveKit credential check → Run workflow → main**.
Workflow: `.github/workflows/livekit-credential-check.yml`.

### Native iOS signing prerequisite — compile PASS; entitlement check BLOCKED

The `ios/` Xcode project is a prerequisite probe with a static explanatory screen.
It imports the public SwiftUI, PushToTalk, and AVFoundation frameworks and declares
only the required PushToTalk/APNs entitlements plus the PushToTalk background mode.
It starts no channel, microphone, audio session, or network connection. It is not a
PTT candidate and must not be used for F1–F7 acceptance.

[Unsigned archive run 2](https://github.com/GurthBro0ks/slime_talk/actions/runs/36257718911)
passed at commit `a3ba693b65c053b88293c21618cb3eec3d9714dd` using Xcode 26.3
and the native arm64 iPhoneOS target. This was not a simulator run.

- Xcode project and plist validation: PASS.
- Native application archive compilation with signing disabled: PASS.
- Temporary build products removed; no artifacts uploaded.
- The first attempt failed before compilation due to an empty-array/`nounset`
  incompatibility in macOS Bash 3.2; the wrapper was fixed and re-tested.

Local reproduction on a Mac with Xcode 26.3:

```sh
export DEVELOPER_DIR=/Applications/Xcode_26.3.app/Contents/Developer
export RUNNER_TEMP="$(mktemp -d)"
bash ci/archive_probe.sh
```

Workflow: `.github/workflows/ios-signing-probe.yml`. Pushes compile without credentials.
Manual dispatch compiles first, then requests the protected environment review for
a separate signing job. That job rebuilds before receiving the API key, exports
using Xcode cloud signing, and checks the signed app and embedded profile for:

- exact bundle/team/application identifiers;
- PushToTalk permitted in both app signature and profile;
- production APNs in both app signature and profile;
- non-debug, unexpired App Store beta distribution provisioning;
- valid application code signature.

[Manual signing run 3](https://github.com/GurthBro0ks/slime_talk/actions/runs/36257775576)
ran at the same source commit after owner environment approval.

- Both unsigned compile jobs passed.
- Xcode export returned success and exactly one IPA was found.
- Exported application signature integrity verification passed; signed entitlements
  and the embedded profile decoded successfully. These observations follow from
  reaching the subsequent failing assertion in the committed verifier.
- Bundle ID and PushToTalk background-mode check passed.
- **FAIL:** `PushToTalk entitlement is missing or not permitted; stop for provisioning review.`
- The assertion checks the signed app and profile in sequence using the same message.
  The log does not identify which failed. Later APNs/distribution checks were not completed.
- A read-only portal refresh confirmed Push to Talk and Push Notifications remain enabled.
- The Certificates page shows an API-created Distribution Managed certificate,
  expiry 2027-09-26. The normal Profiles list shows no entries; that observation
  does not establish the absence of Xcode-managed provisioning.
- Temporary key, raw export log, IPA, and build products were removed. No signing
  artifacts or credentials were uploaded to GitHub; no TestFlight upload occurred.
- The API key was masked in Actions logs; no unexpected raw base64 line was detected.

Engineering stopped under the owner's provisioning stop condition. Recommend a
Canonical PM-authorized diagnostic repair that separately reports entitlement presence
in the signed app and profile and investigates entitlement preservation in the
unsigned archive/export path. Do not bypass the checks or remove required entitlements.
This result does not establish Apple/LiveKit architectural incompatibility.

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
remains open at this inspection. The reporter clarified that their integration uses
custom PTT rather than Apple's PTChannelManager or CallKit. A maintainer reported
successful receive-only playback in the Swift example and requested the integration
conditions. Reports that recording-always-prepared mode masks the issue are not an
acceptable feasibility workaround. F4 must still be measured with no prior mic activation.
These upstream reports do not prove this candidate will pass or fail.

## Evidence boundaries

Never infer latency or microphone shutdown from UI state alone. Do not record speech
content or publish credentials, private-device identifiers, APNs device tokens, or
personal account information in this public repository or its logs. Store only
redacted evidence. Application-level E2EE is outside the approved feasibility scope.

Overall feasibility result: BLOCKED pending setup; architecture remains unproven.
