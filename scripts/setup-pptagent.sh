#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
exec bash "$PROJECT_ROOT/scripts/setup-pptagent-$PPTAGENT_OS.sh" "$@"
