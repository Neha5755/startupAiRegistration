"""Vercel serverless API for StartupReady AI.

The browser keeps a draft in localStorage. This endpoint validates auto-save
requests and is intentionally stateless until a production database is added.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Handle health and registration API requests on Vercel."""

    def send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.endswith("/health"):
            self.send_json(HTTPStatus.OK, {"ok": True, "language": "Python", "deployment": "Vercel"})
        elif self.path.startswith("/api/"):
            self.send_json(HTTPStatus.OK, {"data": {}, "savedAt": None})
        else:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        if not self.path.startswith("/api/"):
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1_000_000:
                self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request is too large."})
                return
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload.get("data"), dict):
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "A data object is required."})
                return
            saved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            self.send_json(HTTPStatus.OK, {"data": payload["data"], "savedAt": saved_at})
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON."})

    def log_message(self, format_string: str, *args) -> None:
        return
