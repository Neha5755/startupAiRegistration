"""StartupReady AI registration API and static-file server.

This backend intentionally uses only the Python standard library so it can run
in a Python full-stack internship environment without extra dependencies.
"""

from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIRECTORY / "registration.json"
PORT = int(os.environ.get("PORT", "3000"))


def read_registration() -> dict:
    """Return saved registration data, or an empty registration record."""
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"data": {}, "savedAt": None}


def save_registration(data: dict) -> dict:
    """Persist a registration record and return the saved representation."""
    DATA_DIRECTORY.mkdir(exist_ok=True)
    record = {
        "data": data,
        "savedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    DATA_FILE.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


class StartupReadyHandler(SimpleHTTPRequestHandler):
    """Serve the frontend plus small JSON endpoints used for auto-save."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json(HTTPStatus.OK, {"ok": True, "language": "Python"})
            return
        if path == "/api/registration":
            self.send_json(HTTPStatus.OK, read_registration())
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/registration":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1_000_000:
                self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request is too large."})
                return
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            data = payload.get("data")
            if not isinstance(data, dict):
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "A data object is required."})
                return
            self.send_json(HTTPStatus.OK, save_registration(data))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON."})

    def log_message(self, format_string: str, *args) -> None:
        print(f"[Python API] {self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    mimetypes.add_type("application/javascript", ".js")
    server = ThreadingHTTPServer(("", PORT), StartupReadyHandler)
    print(f"StartupReady AI Python server is running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
