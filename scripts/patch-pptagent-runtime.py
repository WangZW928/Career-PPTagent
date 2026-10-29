#!/usr/bin/env python3
"""Allow the pinned macOS converter to use this project's Playwright Chromium."""
from importlib.util import find_spec
from pathlib import Path

spec = find_spec("deeppresenter")
if spec is None or not spec.submodule_search_locations:
    raise SystemExit("Run this script using the PPTAgent virtual environment")
package = Path(next(iter(spec.submodule_search_locations)))


def apply(path: Path, originals: list[str], patched: str) -> None:
    source = path.read_text()
    if patched in source:
        print(f"Chromium patch already applied: {path.name}")
        return
    for original in originals:
        if source.count(original) == 1:
            path.write_text(source.replace(original, patched, 1))
            print(f"Applied Chromium patch: {path.name}")
            return
    raise SystemExit(f"Runtime changed; review its browser launch before patching: {path}")


apply(
    package / "html2pptx/html2pptx.js",
    ["if (process.platform === 'darwin') {\n      launchOptions.channel = 'chrome';",
     "if (process.platform === 'darwin' && !process.env.PPTAGENT_USE_BUNDLED_CHROMIUM) {\n      launchOptions.channel = 'chrome';"],
    "if (process.env.PPTAGENT_USE_BUNDLED_CHROMIUM) {\n"
    "      launchOptions.channel = 'chromium';\n"
    "    } else if (process.platform === 'darwin') {\n"
    "      launchOptions.channel = 'chrome';",
)
webview = package / "utils/webview.py"
source = webview.read_text()
if "import os\n" not in source:
    if not source.startswith("import asyncio\n"):
        raise SystemExit("Review changed webview imports before patching")
    webview.write_text(source.replace("import asyncio\n", "import asyncio\nimport os\n", 1))
apply(
    webview,
    ["headless=True, args=LAUNCH_ARGS"],
    "headless=True, args=LAUNCH_ARGS,\n"
    "                        channel=('chromium' if os.environ.get('PPTAGENT_USE_BUNDLED_CHROMIUM') else None)",
)
