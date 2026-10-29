#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
cd "$PROJECT_ROOT"
mkdir -p "$PPTAGENT_RUNTIME/illustrations"
cp tools/illustrations/package.json tools/illustrations/package-lock.json "$PPTAGENT_RUNTIME/illustrations/"
npm ci --prefix "$PPTAGENT_RUNTIME/illustrations" --cache "$PPTAGENT_RUNTIME/npm-cache" --no-audit --no-fund
bin/agentdraw doctor --json
