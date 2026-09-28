#!/usr/bin/env bash
set -euo pipefail
test "${GITHUB_RUN_ATTEMPT:-1}" = 1
test "$(git rev-parse HEAD)" = "$GITHUB_SHA"
baseline=c16987116823f5f96fd7e09e2f0b02efc2c20dfc
git cat-file -e "$baseline^{commit}"
git diff --exit-code "$baseline" HEAD -- ios android controller ':!controller/test' >/dev/null
echo "BUILD_17_SOURCE=$baseline"
echo 'RUNTIME_IDENTITY=byte-identical; controller tests excluded'
