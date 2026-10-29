#!/usr/bin/env python3
"""Connect project skills to a configured Paper2Any or self-hosted ComfyUI API."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "paper2any": ("PAPER2ANY", "/openapi.json", "X-API-Key"),
    "comfyui": ("COMFYUI", "/system_stats", "Authorization"),
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_env() -> None:
    env_file = ROOT / ".env.illustrations"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
                os.environ.setdefault(key, value.strip().strip("\"'"))


def settings(service: str) -> tuple[str, dict]:
    prefix, _, default_header = SERVICES[service]
    base = os.environ.get(prefix + "_URL", "").strip().rstrip("/")
    if not base:
        raise ValueError(f"not_configured: set {prefix}_URL in .env.illustrations")
    parsed = urlsplit(base)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"Invalid {prefix}_URL; use an HTTP(S) service base URL without credentials or query")
    headers = {"Accept": "application/json"}
    key = os.environ.get(prefix + "_API_KEY", "")
    if key:
        header = os.environ.get(prefix + "_API_KEY_HEADER") or default_header
        if not re.fullmatch(r"[A-Za-z0-9-]+", header):
            raise ValueError("Invalid API key header name")
        headers[header] = ("Bearer " + key) if header.lower() == "authorization" else key
    return base, headers


def request(service: str, path: str, method="GET", payload=None, timeout=30):
    base, headers = settings(service)
    parsed = urlsplit(path)
    if not path.startswith("/") or path.startswith("//") or parsed.scheme or parsed.netloc or parsed.fragment:
        raise ValueError("Use a relative API path starting with / on the configured service")
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        headers["Content-Type"] = "application/json"
    req = Request(base + path, data=data, headers=headers, method=method)
    try:
        with build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except HTTPError as error:
        # Avoid printing backend bodies or URLs that could echo keys or source files.
        raise RuntimeError(f"{service} returned HTTP {error.code}; check the endpoint and authentication") from None
    except URLError:
        raise RuntimeError(f"{service} is unreachable; check its URL and whether the service is running") from None


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("service", choices=SERVICES)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    schema = sub.add_parser("schema")
    schema.add_argument("--out", type=Path)
    call = sub.add_parser("request")
    call.add_argument("path")
    call.add_argument("--method", choices=["GET", "POST"], default="GET")
    call.add_argument("--json-file", type=Path)
    call.add_argument("--out", type=Path)
    call.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            raw, _ = request(args.service, SERVICES[args.service][1], timeout=5)
            result = json.loads(raw)
            if not isinstance(result, dict) or (args.service == "paper2any" and not ("openapi" in result and "paths" in result)) or (args.service == "comfyui" and not ("system" in result and "devices" in result)):
                raise ValueError("Unexpected service response; check the configured base URL")
            print(json.dumps({"ok": True, "service": args.service, "status": "api_available", "generation_tested": False}))
            return
        path = ("/object_info" if args.service == "comfyui" else "/openapi.json") if args.command == "schema" else args.path
        payload = json.loads(args.json_file.read_text()) if args.command == "request" and args.json_file else None
        if args.command == "request" and payload is not None and args.method != "POST":
            raise ValueError("--json-file requires --method POST")
        timeout = args.timeout if args.command == "request" else 30
        if not 0 < timeout <= 600:
            raise ValueError("--timeout must be between 0 and 600 seconds")
        data, content_type = request(args.service, path, getattr(args, "method", "GET"), payload, timeout)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_bytes(data)
            print(json.dumps({"ok": True, "file": str(args.out), "bytes": len(data)}))
        elif "json" in content_type:
            print(json.dumps(json.loads(data), ensure_ascii=False, indent=2))
        else:
            raise ValueError("Response is not JSON; use --out to save the artifact")
    except (ValueError, OSError, RuntimeError) as error:
        status = "not_configured" if str(error).startswith("not_configured:") else "error"
        print(json.dumps({"ok": False, "service": args.service, "status": status, "error": str(error)}, ensure_ascii=False))
        sys.exit(2 if status == "not_configured" else 1)


if __name__ == "__main__":
    main()
