#!/usr/bin/env python3
"""Capture a local HTML/SVG illustration using the project's Chromium."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--scale", type=float, default=2)
    parser.add_argument("--wait-ms", type=int, default=1500)
    parser.add_argument("--query", default="", help="Figure state, e.g. yaw=45&xr=1")
    parser.add_argument("--selector", help="Capture a specific element, e.g. #fig")
    parser.add_argument("--hide-selector", action="append", default=[], help="Hide matching overlays before capture; repeat as needed")
    parser.add_argument("--omit-background", action="store_true")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.out.resolve()
    if not source.is_file() or source.suffix.lower() not in {".html", ".htm", ".svg"}:
        parser.error("source must be an existing local HTML or SVG file")
    if output.suffix.lower() != ".png":
        parser.error("--out must end in .png")
    if not (1 <= args.width <= 8192 and 1 <= args.height <= 8192 and 0 < args.scale <= 4):
        parser.error("invalid viewport or scale")
    if not 0 <= args.wait_ms <= 60000:
        parser.error("--wait-ms must be between 0 and 60000")
    errors, blocked = [], []
    output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chromium", headless=True)
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        page.on("pageerror", lambda error: errors.append(str(error)))

        def local_only(route):
            if urlsplit(route.request.url).scheme in {"file", "data", "blob"}:
                route.continue_()
            else:
                blocked.append(urlsplit(route.request.url).netloc)
                route.abort()

        page.route("**/*", local_only)
        url = source.as_uri() + ("?" + args.query.lstrip("?") if args.query else "")
        try:
            page.goto(url, wait_until="load", timeout=30000)
            page.evaluate("() => document.fonts.ready.then(() => true)")
            page.wait_for_timeout(args.wait_ms)
            figure_errors = page.locator("html").get_attribute("data-errors")
            if figure_errors:
                errors.append(figure_errors)
            if errors or blocked:
                raise RuntimeError(json.dumps({"page_errors": errors, "blocked_hosts": sorted(set(blocked))}))
            for selector in args.hide_selector:
                page.locator(selector).evaluate_all("elements => elements.forEach(el => el.style.setProperty('visibility', 'hidden', 'important'))")
            target = page.locator(args.selector) if args.selector else page
            target.screenshot(path=str(output), omit_background=args.omit_background)
        finally:
            browser.close()
    print(json.dumps({"ok": True, "source": str(source), "png": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
