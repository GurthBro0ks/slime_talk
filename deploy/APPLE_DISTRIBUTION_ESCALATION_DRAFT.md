# Apple Developer Support / Feedback Assistant — draft, not submitted

Subject: TestFlight upload command accepted, but internal build availability not established — app 6816454718, version 0.1.0 (17)

We request help locating and diagnosing an App Store Connect upload for our iOS feasibility app. We made one controlled upload of build 17 after an earlier build 16 upload had transport acceptance but no matching build resource or visible TestFlight build. We have stopped further upload attempts.

## Safe diagnostic metadata

- App ID: 6816454718
- Bundle ID: ai.slimy.slimetalk.feasibility
- Version/build: 0.1.0 (17)
- Frozen runtime source: c16987116823f5f96fd7e09e2f0b02efc2c20dfc
- Workflow source: 4aeb9473b859b88c5f2f5a3ab99aa960a83696da
- CI run: https://github.com/GurthBro0ks/slime_talk/actions/runs/36469738250
- Build environment: macOS-15 GitHub-hosted runner, selected Xcode 26.3
- Upload tool: xcrun altool --upload-app, iOS, JSON output; existing API-key authentication, with credentials omitted here
- Exactly one build-17 upload; no build 18 or additional retry

- Upload transport result: accepted
- Exact runner post-command timestamp: 2026-09-28T19:14:57.639578+00:00 (not an Apple server receipt timestamp)
- IPA SHA-256: `b6006d3ed50c2ade68b59cd224be1a884a963e281a8b8b27ebfe774ae85d65be`
- Request-ID extractor output: `not_returned`; no recoverable request/delivery/upload identifier in retained sanitized logs. The restricted extractor does not prove the raw response lacked every possible identifier.
- Upload record/state: unavailable; the upload-record endpoint was not queried by this build-17 workflow
- Bounded read-only build queries: 20 successful complete filtered responses, 2026-09-28T19:14:58.794Z through 2026-09-28T19:34:02.049Z
- App identity match: yes; all responses found no exact 0.1.0/build 17 resource
- Build resource ID: none found; processing state: unknown
- Build17 API HTTP/authorization errors: none reported
- Explicit Apple FAILED/INVALID processing result: not observed
- Authenticated TestFlight UI after poll: No Builds; internal installability not established
- CI completed: 2026-09-28T19:34:06Z, conclusion failure because availability criterion was unmet, not an Apple rejection
- Verification passed: frozen runtime identity; Swift/controller/source safety; automatic archive and export signatures; archive/export PushToTalk; exported production APNs; matching app/team identifiers; current non-debug App Store distribution profile
- Automatic archive used development APNs/profile; exported distribution output used production APNs/App Store profile. Both signature and entitlement checks passed.
- Private signing/output cleanup succeeded; no IPA/raw response artifact was retained

Historical context: build16 transport was accepted, but no matching build or usable TestFlight listing was established. Its separate upload-record diagnostic returned a scope-related 403. That earlier endpoint error is not a build17 authorization error. No upload-resource state is asserted for either build.

## Request to Apple

Please correlate the upload using the metadata supplied and identify its server-side upload record, receipt/processing state, and any actionable validation or ingestion error. Please explain why internal TestFlight availability has not been established and what diagnostic action is appropriate without another upload. If owner attestation or an account action is required, provide the exact question for the account holder.

Transport acceptance is not a claim of successful processing. A missing build resource or the TestFlight “No Builds” UI is not, by itself, proof of upload failure. We do not currently assert a processing duration over 24 hours.

No credentials, authentication tokens, signing keys, provisioning profiles, raw Apple responses, IPA binary, device pairing keys, phone identifiers, or personal account contact data are included. Raw upload output was deliberately not retained as a CI artifact. This draft has not been submitted.
