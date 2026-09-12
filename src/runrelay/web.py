from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .service import RunRelayService


def serve(service: RunRelayService, host: str, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if urlparse(self.path).path == "/api/experiments":
                body = json.dumps(
                    [item.to_dict() for item in service.list()],
                    ensure_ascii=False,
                ).encode()
                content_type = "application/json; charset=utf-8"
            else:
                body = _page(service)
                content_type = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"RunRelay dashboard: http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _page(service: RunRelayService) -> bytes:
    rows = []
    for item in service.list():
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(item.id)}</code></td>"
            f"<td>{html.escape(item.host)}</td>"
            f"<td><strong>{html.escape(item.status.value)}</strong></td>"
            f"<td><code>{html.escape(item.command)}</code></td>"
            "</tr>"
        )
    return (
        "<!doctype html><meta charset='utf-8'><meta http-equiv='refresh' content='5'>"
        "<title>RunRelay</title><style>body{font:15px system-ui;margin:2rem}"
        "table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;"
        "padding:.6rem;text-align:left}code{white-space:pre-wrap}</style>"
        "<h1>RunRelay experiments</h1><table><tr><th>ID</th><th>Host</th>"
        "<th>Status</th><th>Command</th></tr>"
        + "".join(rows)
        + "</table>"
    ).encode()

