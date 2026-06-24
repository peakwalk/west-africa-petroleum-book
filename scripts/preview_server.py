#!/usr/bin/env python3
"""Serve preview assets with no-cache headers for HTML documents only."""

from __future__ import annotations

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class PreviewRequestHandler(SimpleHTTPRequestHandler):
    def _is_html_request(self) -> bool:
        request_path = urlsplit(self.path).path
        local_path = Path(self.translate_path(request_path))

        if local_path.is_dir():
            local_path = local_path / "index.html"

        return local_path.suffix.lower() == ".html" and local_path.exists()

    def end_headers(self) -> None:
        if self._is_html_request():
            self.send_header("Cache-Control", "no-store, max-age=0, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the built preview with HTML no-cache headers."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--display-host")
    parser.add_argument("--port", type=int, default=3002)
    parser.add_argument("--directory", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handler = functools.partial(PreviewRequestHandler, directory=args.directory)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    display_host = args.display_host or args.host

    print(
        f"Serving preview on http://{display_host}:{args.port}/ from {args.directory}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
