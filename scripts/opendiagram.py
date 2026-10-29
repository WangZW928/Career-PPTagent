#!/usr/bin/env python3
"""Run the pinned OpenDiagram engine locally and export editable/PPT assets."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    render = sub.add_parser('render')
    render.add_argument('spec', type=Path)
    render.add_argument('--out', required=True, type=Path, help='Output basename (no extension)')
    render.add_argument('--theme', choices=['classic', 'sketch'], default='classic')
    args = parser.parse_args()
    runtime = Path(os.environ['PPTAGENT_RUNTIME']) / 'opendiagram'
    checks = {name: (runtime / name).is_file() for name in ('layout.ts', 'browser.js', 'node_modules/.bin/tsx', 'harness/src/index.ts')}
    if args.command == 'doctor':
        print(json.dumps({'ok': all(checks.values()), 'checks': checks, 'mode': 'local-harness', 'web_app_deployed': False}))
        raise SystemExit(0 if all(checks.values()) else 1)
    if not all(checks.values()):
        parser.error('Run scripts/setup-opendiagram.sh first')
    output = args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='export-', dir=runtime) as temp:
        folder = Path(temp)
        layout = folder / 'layout.json'
        subprocess.run([str(runtime / 'node_modules/.bin/tsx'), str(runtime / 'layout.ts'), str(args.spec.resolve()), str(layout), args.theme], check=True)
        rendered = json.loads(layout.read_text())
        page_file = folder / 'export.html'
        page_file.write_text('<!doctype html><meta charset="utf-8"><script>window.EXCALIDRAW_ASSET_PATH="https://opendiagram.local/";</script><script src="/browser.js"></script>')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='chromium', headless=True)
            page = browser.new_page(device_scale_factor=2)
            blocked = []
            def local_only(route):
                if route.request.url.startswith('https://opendiagram.local/'):
                    from urllib.parse import unquote, urlsplit
                    path = (runtime / unquote(urlsplit(route.request.url).path).lstrip('/')).resolve()
                    if path.is_relative_to(runtime.resolve()) and path.is_file():
                        route.fulfill(path=str(path))
                    else:
                        route.fulfill(status=404, body='Local asset missing')
                elif route.request.url.startswith(('file:', 'data:', 'blob:')):
                    route.continue_()
                else:
                    blocked.append(route.request.url.split('/')[2])
                    route.abort()
            page.route('**/*', local_only)
            page.goto('https://opendiagram.local/' + page_file.relative_to(runtime).as_posix())
            result = page.evaluate('(r) => window.exportDiagram(r)', rendered)
            if blocked:
                raise RuntimeError(f'External resources blocked: {sorted(set(blocked))}')
            svg = Path(str(output) + '.svg')
            svg.write_text(result['svg'])
            Path(str(output) + '.excalidraw').write_text(result['scene'])
            page.goto(svg.as_uri())
            page.evaluate('() => document.fonts.ready')
            page.locator('svg').screenshot(path=str(output) + '.png')
            browser.close()
    Path(str(output) + '.spec.json').write_text(args.spec.read_text())
    report = {'ok': True, 'elements': result['count'], 'warnings': rendered['warnings'], 'outputs': [str(output) + suffix for suffix in ('.svg', '.png', '.excalidraw', '.spec.json')]}
    Path(str(output) + '.report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
