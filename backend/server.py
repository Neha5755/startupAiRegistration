"""Python server for the Channapatna Gifts catalogue and order requests."""

from __future__ import annotations

import json
import mimetypes
import os
import re
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
UPLOAD_DIRECTORY = DATA_DIRECTORY / "uploads"
ORDERS_FILE = DATA_DIRECTORY / "orders.json"
PORT = int(os.environ.get("PORT", "3000"))
MAX_REQUEST_SIZE = 30 * 1024 * 1024
MAX_FILE_SIZE = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf", ".mp4", ".mov", ".webm"}


def read_orders() -> list[dict]:
    try:
        return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_order(order: dict) -> None:
    DATA_DIRECTORY.mkdir(exist_ok=True)
    orders = read_orders()
    orders.append(order)
    ORDERS_FILE.write_text(json.dumps(orders, indent=2), encoding="utf-8")


def safe_filename(name: str) -> str:
    base = Path(name).name
    return re.sub(r"[^A-Za-z0-9._-]", "_", base)


def parse_multipart(content_type: str, body: bytes) -> tuple[dict[str, str], list[tuple[str, bytes]]]:
    """Parse browser FormData without third-party dependencies."""
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    fields: dict[str, str] = {}
    files: list[tuple[str, bytes]] = []
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        field_name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename:
            files.append((safe_filename(filename), payload))
        elif field_name:
            fields[field_name] = payload.decode("utf-8", errors="replace").strip()
    return fields, files


class GiftHandler(SimpleHTTPRequestHandler):
    """Serve the catalogue and accept custom order requests."""

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
        if urlparse(self.path).path == "/api/health":
            self.send_json(HTTPStatus.OK, {"ok": True, "language": "Python"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/orders":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", "0"))
        if not content_type.startswith("multipart/form-data"):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Use the custom order form to send this request."})
            return
        if not content_length or content_length > MAX_REQUEST_SIZE:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Your total upload must be below 30 MB."})
            return
        try:
            fields, uploads = parse_multipart(content_type, self.rfile.read(content_length))
            if not all(fields.get(key) for key in ("name", "email", "product")):
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Name, email, and product are required."})
                return
            if "@" not in fields["email"]:
                self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Please enter a valid email address."})
                return
            UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
            uploaded_names = []
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            for filename, content in uploads:
                extension = Path(filename).suffix.lower()
                if extension not in ALLOWED_EXTENSIONS or len(content) > MAX_FILE_SIZE:
                    self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Files must be images, videos, or PDFs under 8 MB each."})
                    return
                stored_name = f"{stamp}_{filename}"
                (UPLOAD_DIRECTORY / stored_name).write_bytes(content)
                uploaded_names.append(stored_name)
            order = {"id": stamp, "created_at": datetime.now(timezone.utc).isoformat(), "product": fields["product"], "name": fields["name"], "email": fields["email"], "occasion": fields.get("occasion", ""), "needed_by": fields.get("needed_by", ""), "message": fields.get("message", ""), "files": uploaded_names}
            save_order(order)
            self.send_json(HTTPStatus.CREATED, {"ok": True, "message": "Order request received."})
        except (UnicodeDecodeError, ValueError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "We could not read that request. Please try again."})

    def log_message(self, format_string: str, *args) -> None:
        print(f"[Channapatna Gifts] {self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    mimetypes.add_type("application/javascript", ".js")
    server = ThreadingHTTPServer(("", PORT), GiftHandler)
    print(f"Channapatna Gifts is running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
