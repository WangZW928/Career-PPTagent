#!/usr/bin/env python3
"""Install the pinned Playwright browsers using Google's official CFT storage."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import os
import platform
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if platform.system() != 'Darwin' or platform.machine() != 'arm64':
    raise SystemExit('macOS Apple Silicon installer; Linux uses playwright install chromium')
RUNTIME = Path(os.environ['PPTAGENT_RUNTIME'])
DOWNLOADS = RUNTIME / "downloads"
spec = importlib.util.find_spec("playwright")
if spec is None or not spec.submodule_search_locations:
    raise SystemExit("Run with .agents/skills/pptagent/.venv/bin/python")
package = Path(next(iter(spec.submodule_search_locations))) / "driver/package"
descriptors = json.loads((package / "browsers.json").read_text())["browsers"]
browser = next(item for item in descriptors if item["name"] == "chromium")
version, revision = browser["browserVersion"], browser["revision"]
DOWNLOADS.mkdir(parents=True, exist_ok=True)


def download(filename: str) -> Path:
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/mac-arm64/{filename}"
    archive = DOWNLOADS / filename
    header = subprocess.check_output(
        ["curl", "-fsSI", "--connect-timeout", "15", "--max-time", "45", url],
        text=True,
    )
    length = int(re.findall(r"(?im)^content-length:\s*(\d+)", header)[-1])
    downloaded = archive.stat().st_size if archive.exists() else 0
    if downloaded > length:
        raise SystemExit(f"Unexpected archive size: {archive}")
    parts_dir = DOWNLOADS / (filename + ".parts")
    parts_dir.mkdir(exist_ok=True)
    # Each worker writes a separate file. Merge only complete, verified ranges.
    chunk = 8 * 1024 * 1024
    ranges = [(start, min(start + chunk, length) - 1) for start in range(downloaded, length, chunk)]

    def part(bounds: tuple[int, int]) -> tuple[int, Path]:
        start, end = bounds
        destination = parts_dir / f"{start}-{end}"
        if not destination.exists() or destination.stat().st_size != end - start + 1:
            subprocess.run(
                ["curl", "-fsSL", "--retry", "2", "--connect-timeout", "15",
                 "--max-time", "240", "--range", f"{start}-{end}",
                 "--output", str(destination), f"{url}?pptagent_range={start}"],
                check=True,
            )
        if destination.stat().st_size != end - start + 1:
            raise ValueError(f"Server did not return requested range: {destination}")
        print(f"Downloaded {filename}: bytes {start}-{end}", flush=True)
        return start, destination

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(part, bounds) for bounds in ranges]
        parts = dict(future.result() for future in as_completed(futures))
    if ranges:
        with archive.open("ab") as handle:
            for start, _ in ranges:
                with parts[start].open("rb") as source:
                    while block := source.read(1024 * 1024):
                        handle.write(block)
    with zipfile.ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad:
            raise ValueError(f"Archive CRC failed: {bad}")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {filename}\n")
    return archive


for name, filename in [("chromium", "chrome-mac-arm64.zip")]:
    target = RUNTIME / "browsers" / f"{name}-{revision}"
    if (target / "INSTALLATION_COMPLETE").is_file():
        print(f"Already installed: {target}", flush=True)
        continue
    archive = download(filename)
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ditto", "-x", "-k", str(archive), str(target)], check=True)
    (target / "INSTALLATION_COMPLETE").touch()
    print(f"Installed: {target}", flush=True)

print(json.dumps({"ok": True, "browser_version": version, "revision": revision}))
