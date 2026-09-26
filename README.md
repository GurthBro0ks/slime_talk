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
- Signing identities and provisioning profiles are not yet created or verified.
- LiveKit is at the sign-in/registration page; no project or billing setup has been created.

The owner authorized only the minimum feasibility App ID/capabilities, signing,
provisioning, APNs, free LiveKit project, hosted signed builds, and TestFlight path.
No purchases, paid infrastructure, unrelated capabilities, or production build are authorized.

### Current setup blockers

1. App Store Connect API access is not enabled. The Account Holder must review
   Apple's separate internal-use agreement and submit the access request before
   CI credentials can be created. The request dialog is prepared but NOT submitted.
   Engineering stopped at the owner's explicit approval/decision boundary.
2. LiveKit requires owner sign-in or registration (including any signup terms).
   Only the authorized free Build project is permitted.
3. Controller hosting endpoint/access and physical-device test coordination remain
   unresolved; the prototype has not been implemented.

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
