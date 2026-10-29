#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
[[ "$PPTAGENT_PLATFORM" == macos-arm64 ]] || { echo 'macOS installer requires Apple Silicon' >&2; exit 1; }
for dependency in curl ditto hdiutil; do
  command -v "$dependency" >/dev/null || { echo "Missing dependency: $dependency" >&2; exit 1; }
done
bash "$PROJECT_ROOT/scripts/setup-pptagent-common.sh"
"$PPTAGENT_PYTHON" "$PROJECT_ROOT/scripts/install-pptagent-browsers.py"
"$PPTAGENT_PYTHON" "$PROJECT_ROOT/scripts/install-pptagent-libreoffice.py"
"$PROJECT_ROOT/bin/pptagent" doctor
