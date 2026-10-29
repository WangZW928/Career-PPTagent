#!/bin/bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/runtime-env.sh"
SOURCE="$PROJECT_ROOT/.runtime/sources/OpenDiagram"
REVISION=d09e61d1818f022b689255dc60425a422f9c1b0b
if [[ ! -d "$SOURCE/.git" ]]; then
  git clone https://github.com/Itz-Agasta/OpenDiagram.git "$SOURCE"
fi
if [[ "$(git -C "$SOURCE" rev-parse HEAD)" != "$REVISION" ]]; then
  git -C "$SOURCE" fetch origin "$REVISION"
  git -C "$SOURCE" checkout --detach "$REVISION"
fi
DEST="$PPTAGENT_RUNTIME/opendiagram"
mkdir -p "$DEST"
cp "$PROJECT_ROOT/tools/opendiagram/package.json" "$PROJECT_ROOT/tools/opendiagram/package-lock.json" "$DEST/"
cp -R "$SOURCE/packages/harness" "$DEST/"
cp "$SOURCE/apps/web/src/lib/excalidraw-utils.ts" "$SOURCE/LICENSE" "$DEST/"
cp "$PROJECT_ROOT/tools/opendiagram/layout.ts" "$PROJECT_ROOT/tools/opendiagram/browser.ts" "$DEST/"
npm ci --prefix "$DEST" --cache "$PPTAGENT_RUNTIME/npm-cache" --no-audit --no-fund
"$DEST/node_modules/.bin/esbuild" "$DEST/browser.ts" --bundle --format=iife --platform=browser --define:process.env.NODE_ENV='"production"' --outfile="$DEST/browser.js"
cp -R "$DEST/node_modules/@excalidraw/excalidraw/dist/prod/fonts" "$DEST/"
"$PROJECT_ROOT/bin/opendiagram" doctor
