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

1. Apple CI credential check run `36256889270` is waiting for the owner's review of
   the protected `ios-feasibility-signing` environment. The key transfer is complete.
   The private-key value must never be sent in chat or published.
2. Signing and PushToTalk provisioning still need verification on an actual signed archive.
3. Controller hosting endpoint/access and physical-device test coordination remain
   unresolved; the clients and controller have not been implemented.

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
The automatic signing path remains an experiment; it has not yet produced a certificate,
provisioning profile, or signed archive.

### Apple CI credential validation (waiting for environment review)

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
- Actual stored-key/Apple API check: NOT RUN; [run 1](https://github.com/GurthBro0ks/slime_talk/actions/runs/36256889270)
  is waiting for owner environment review at commit `26157d76e6e861c45c4724d0b73bc0da305dd595`.

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
