#!/usr/bin/env python3
"""Install LibreOffice in this project, with the official cask SHA-256."""
import hashlib
import os
from pathlib import Path
import platform
import subprocess

if platform.system() != "Darwin" or platform.machine() != "arm64":
    raise SystemExit("This local installer targets macOS Apple Silicon")
runtime = Path(os.environ['PPTAGENT_RUNTIME'])
app = runtime / "apps/LibreOffice.app"


def link_chinese_fonts() -> None:
    # Headless LibreOffice on this Mac does not discover system CJK fonts.
    # Link existing OS fonts into the project app's scanned font directory.
    target_dir = app / "Contents/Resources/fonts/truetype"
    for name in ("STHeiti Light.ttc", "STHeiti Medium.ttc"):
        source = Path("/System/Library/Fonts") / name
        if not source.is_file():
            raise SystemExit(f"Required macOS Chinese font missing: {source}")
        target = target_dir / name
        if not target.exists():
            target.symlink_to(source)
    print("Project LibreOffice Chinese fonts configured")


if (app / "Contents/MacOS/soffice").is_file():
    link_chinese_fonts()
    print("Project LibreOffice already installed")
    raise SystemExit(0)
filename = "LibreOffice_26.8.1_MacOS_aarch64.dmg"
digest = "ca074e0b13571efb30a31fc531c5f95e997030637325e5d5de92d67aefdf0dfc"
archive = runtime / "downloads" / filename
archive.parent.mkdir(parents=True, exist_ok=True)
if not archive.is_file():
    subprocess.run(
        ["curl", "-fL", "--retry", "2", "--connect-timeout", "20", "--max-time", "600",
         "--output", str(archive),
         f"https://download.documentfoundation.org/libreoffice/stable/26.8.1/mac/aarch64/{filename}"],
        check=True,
    )
with archive.open("rb") as handle:
    actual = hashlib.file_digest(handle, "sha256").hexdigest()
if actual != digest:
    raise SystemExit(f"LibreOffice SHA-256 mismatch: {actual}")
mount = runtime / "lo-mount"
mount.mkdir(exist_ok=True)
app.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(
    ["hdiutil", "attach", "-nobrowse", "-readonly", "-mountpoint", str(mount), str(archive)],
    check=True,
)
try:
    subprocess.run(["ditto", str(mount / "LibreOffice.app"), str(app)], check=True)
finally:
    subprocess.run(["hdiutil", "detach", str(mount)], check=True)
link_chinese_fonts()
print(f"Installed {app}")
