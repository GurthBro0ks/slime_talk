#!/usr/bin/env bash
# No credentials are read by this unsigned build step.
set -euo pipefail
set +x
probe_dir="${RUNNER_TEMP:?}/slime-talk-signing-probe"
mkdir -p "$probe_dir"
team_args=()
if [[ -n "${APPLE_TEAM_ID:-}" ]]; then
  [[ "$APPLE_TEAM_ID" =~ ^[A-Z0-9]{10}$ ]] || exit 1
  team_args+=("DEVELOPMENT_TEAM=$APPLE_TEAM_ID")
fi
[[ "${GITHUB_RUN_NUMBER:-1}" =~ ^[0-9]+$ ]] || exit 1
plutil -lint ios/SlimeTalk.xcodeproj/project.pbxproj ios/SlimeTalk/Info.plist ios/SlimeTalk/SlimeTalk.entitlements
xcodebuild -version
if ! xcodebuild archive \
  -project ios/SlimeTalk.xcodeproj -scheme SlimeTalk \
  -configuration Release -destination 'generic/platform=iOS' \
  -archivePath "$probe_dir/SlimeTalk.xcarchive" \
  -derivedDataPath "$probe_dir/DerivedData" \
  CODE_SIGNING_ALLOWED=NO \
  "CURRENT_PROJECT_VERSION=${GITHUB_RUN_NUMBER:-1}" \
  "${team_args[@]}" >"$probe_dir/unsigned-build.log" 2>&1; then
  tail -n 100 "$probe_dir/unsigned-build.log"
  exit 1
fi
test -f "$probe_dir/SlimeTalk.xcarchive/Products/Applications/SlimeTalk.app/SlimeTalk"
echo 'PASS: native arm64 iPhoneOS archive compiled; signing was disabled for this step.'
echo 'No microphone, network transport, simulator, or physical-device test was run.'
