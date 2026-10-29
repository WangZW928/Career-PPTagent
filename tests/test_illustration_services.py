"""Protocol checks against a local fixture server; no model service is called."""
import importlib.util
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("illustration_services", ROOT / "scripts/illustration-services.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class ConnectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                cls.calls.append((self.path, dict(self.headers)))
                if self.path == "/redirect":
                    self.send_response(302)
                    self.send_header("Location", "/must-not-follow")
                    self.end_headers()
                    return
                if self.path.startswith("/view?"):
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    self.wfile.write(b"\x89PNG\r\n\x1a\nfixture")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                payload = {"openapi": "3.1.0", "paths": {}} if self.path == "/openapi.json" else {"system": {}, "devices": []}
                self.wfile.write(json.dumps(payload).encode())

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                cls.calls.append((self.path, payload))
                self.send_response(500 if self.path == "/fail" else 200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"prompt_id": "fixture-id"}).encode())

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_api_headers_submission_and_binary_download(self):
        with patch.dict(os.environ, {"PAPER2ANY_URL": self.base, "PAPER2ANY_API_KEY": "fixture-paper-key", "COMFYUI_URL": self.base, "COMFYUI_API_KEY": "fixture-comfy-key"}, clear=True):
            raw, _ = client.request("paper2any", "/openapi.json")
            self.assertEqual(json.loads(raw)["openapi"], "3.1.0")
            self.assertEqual(self.calls[-1][1]["X-Api-Key"], "fixture-paper-key")
            client.request("comfyui", "/system_stats")
            self.assertEqual(self.calls[-1][1]["Authorization"], "Bearer fixture-comfy-key")
            nodes = {"1": {"class_type": "ExampleNode", "inputs": {}}}
            raw, _ = client.request("comfyui", "/prompt", "POST", {"prompt": nodes})
            self.assertEqual(json.loads(raw)["prompt_id"], "fixture-id")
            self.assertEqual(self.calls[-1][1]["prompt"], nodes)
            raw, content_type = client.request("comfyui", "/view?filename=fixture.png&type=output")
            self.assertEqual(content_type, "image/png")
            self.assertTrue(raw.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_no_cross_host_requests_redirects_or_duplicate_posts(self):
        with patch.dict(os.environ, {"COMFYUI_URL": self.base}, clear=True):
            with self.assertRaises(ValueError):
                client.request("comfyui", "https://other.invalid/view")
            with self.assertRaises(ValueError):
                client.request("comfyui", "//other.invalid/view")
            with self.assertRaises(RuntimeError):
                client.request("comfyui", "/redirect")
            self.assertFalse(any(path == "/must-not-follow" for path, _ in self.calls))
            before = len(self.calls)
            with self.assertRaises(RuntimeError):
                client.request("comfyui", "/fail", "POST", {"prompt": {}})
            self.assertEqual(len(self.calls), before + 1)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "not_configured"):
                client.settings("paper2any")


if __name__ == "__main__":
    unittest.main()
