#!/bin/bash
# Source from project launchers; never share native dependencies across platforms.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
case "$(uname -s)" in
  Linux) PPTAGENT_OS=linux ;;
  Darwin) PPTAGENT_OS=macos ;;
  *) echo 'Supported platforms: Linux and macOS' >&2; return 1 ;;
esac
case "$(uname -m)" in
  x86_64|amd64) PPTAGENT_ARCH=x86_64 ;;
  arm64|aarch64) PPTAGENT_ARCH=arm64 ;;
  *) echo 'Unsupported CPU architecture' >&2; return 1 ;;
esac
export PPTAGENT_PLATFORM="$PPTAGENT_OS-$PPTAGENT_ARCH"
export PPTAGENT_RUNTIME="$PROJECT_ROOT/.runtime/$PPTAGENT_PLATFORM"
export PPTAGENT_PYTHON="$PPTAGENT_RUNTIME/venv/bin/python"
export PPTAGENT_NODE_MODULES="$PPTAGENT_RUNTIME/pptagent-node/node_modules"
export PLAYWRIGHT_BROWSERS_PATH="$PPTAGENT_RUNTIME/browsers"
export PPTAGENT_USE_BUNDLED_CHROMIUM=1
export UV_CACHE_DIR="$PPTAGENT_RUNTIME/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PPTAGENT_RUNTIME/python"
export DCONF_BACKEND=memory

require_pptagent_python() {
  if [[ ! -x "$PPTAGENT_PYTHON" ]]; then
    echo "PPTAgent environment missing for $PPTAGENT_PLATFORM. Run scripts/setup-pptagent.sh." >&2
    return 1
  fi
}
