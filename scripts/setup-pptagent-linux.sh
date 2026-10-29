#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
[[ "$PPTAGENT_OS" == linux ]] || { echo 'Linux only' >&2; exit 1; }
"$PROJECT_ROOT/bin/libreoffice" --version
command -v fc-match >/dev/null || { echo 'Install fontconfig and a Chinese font, e.g. fonts-noto-cjk.' >&2; exit 1; }
if [[ -z "$(fc-list :lang=zh family)" ]]; then
  echo 'Chinese fonts missing. On Debian/Ubuntu: sudo apt-get install fonts-noto-cjk' >&2
  exit 1
fi
bash "$PROJECT_ROOT/scripts/setup-pptagent-common.sh"
"$PPTAGENT_PYTHON" -m playwright install chromium
"$PROJECT_ROOT/bin/pptagent" doctor
