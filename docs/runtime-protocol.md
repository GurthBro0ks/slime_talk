# Phase 0 runtime experiment

Work order SLIME_TALK_FEASIBILITY_003; no production architecture freeze.

One room (`slime-talk-feasibility`), two pre-authorized aliases (`pixel`, `iphone`).
All endpoints are POST JSON over HTTPS. Pairing is only test-device enrollment;
there is no product account/profile/settings system.

- `/login {device,key}`: replace the device's previous session and media participant;
  return a random controller session and receive-only LiveKit join token.
- `/request {requestId}`: serial single-owner grant/deny; grant returns epoch.
- `/renew {epoch}`: validate session/epoch and extend the 4-second server lease.
- `/release {epoch}`: revoke media publish permission before clearing owner.
- `/status {}`: busy/owner/epoch only. All above except login require session bearer.
- `/push {token}`: iPhone-only ephemeral Apple PTT token registration; never logged.

Clients use a conservative **2-second monotonic deadline measured from request
send**, renewing every ~500ms. Expired/slow responses cannot restore an expired
local grant. Server grants have a renewable 4-second lease, not a turn-duration cap.
On uncertain server revocation, the reservation remains blocked until revocation
succeeds. Server startup removes the private room's participants before listening.
Receive join tokens cannot publish data/video/audio; only the controller enables
microphone publishing for the current owner. Media reconnect never requests a grant.

Local VAD observes authorized microphone PCM only. The feasibility classifier uses
RMS > 0.008 plus zero-crossing ratio (0.005,0.45), sustained for 60ms. This is an
explicit experimental speech heuristic, not a claim of accurate speech recognition.
No PCM/content is saved. QA must test silence, quiet speech and background noise.
Capture starts only with a valid local grant (plus valid Apple activation on iOS).
Three seconds without qualifying PCM stops input/capture, publication, and ownership;
no voice-triggered restart exists. Foreground touch cancellation/release clears the
hold. Genuine Apple system begin/end callbacks drive system controls. QA must verify
that after a forced system stop the next begin callback denotes a fresh user action,
and that continued hold never produces reacquisition.

Apple owns AVAudioSession activation. SDK automatic audio-session configuration is
disabled. While inactive both engine directions are disabled; receive activation
allows output only. Input is enabled only for a valid backend grant. No warm-up mic,
recording-always-prepared mode, silent keep-alive, or background foreground simulation
is used. First remote PCM, subscription, engine state, and activation are logged.

All `PTT`/`SLIME_PTT` events include wall time and local monotonic time; do not subtract
monotonic times across phones. Correlate backend epochs and synchronized wall clocks,
and record clock uncertainty for end-to-end measurements. Use physical listening and
external timing evidence for understandable audio/onset loss. Event names represent
requests versus completion explicitly. Android WebRTC hardware capture start/stop
callbacks and iOS synchronous input availability plus engine callbacks must be checked
alongside absence of subsequent PCM and remote audio; UI state is not shutdown proof.

Limitations pending QA: locked activation/reconnect timing, first-frame availability,
VAD errors, lease/permission signal races, real capture shutdown, routes/interruption,
and F1–F7. Successful unit tests/builds do not accept any of these behaviors.
