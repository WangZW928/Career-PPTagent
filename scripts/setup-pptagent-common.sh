#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
cd "$PROJECT_ROOT"
for dependency in uv node npm; do
  command -v "$dependency" >/dev/null || { echo "Missing dependency: $dependency" >&2; exit 1; }
done
mkdir -p "$PPTAGENT_RUNTIME/pptagent-node"
if [[ ! -x "$PPTAGENT_PYTHON" ]]; then
  uv venv --python 3.12 "$PPTAGENT_RUNTIME/venv"
fi
uv pip install --python "$PPTAGENT_PYTHON" -r "$PROJECT_ROOT/requirements-pptagent.lock"
cp .agents/skills/pptagent/package.json .agents/skills/pptagent/package-lock.json "$PPTAGENT_RUNTIME/pptagent-node/"
npm ci --prefix "$PPTAGENT_RUNTIME/pptagent-node" --cache "$PPTAGENT_RUNTIME/npm-cache" --no-audit --no-fund
"$PPTAGENT_PYTHON" scripts/patch-pptagent-runtime.py
