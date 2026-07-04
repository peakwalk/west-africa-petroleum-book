#!/usr/bin/env python3
"""Serve preview assets with no-cache headers for HTML documents only."""

from __future__ import annotations

import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class PreviewRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, reload_token_file: str | None = None, **kwargs):
        self.reload_token_file = Path(reload_token_file) if reload_token_file else None
        super().__init__(*args, **kwargs)

    def _resolve_local_path(self) -> tuple[str, Path]:
        request_path = urlsplit(self.path).path
        local_path = Path(self.translate_path(request_path))

        if local_path.is_dir():
            index_path = local_path / "index.html"
            if index_path.exists():
                local_path = index_path

        return request_path, local_path

    def _is_html_request(self) -> bool:
        _, local_path = self._resolve_local_path()
        return local_path.suffix.lower() == ".html" and local_path.exists()

    def _read_reload_token(self) -> str:
        if not self.reload_token_file:
            return ""

        try:
            return self.reload_token_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""

    def _inject_preview_reload_helper(self, html_text: str) -> str:
        reload_token = json.dumps(self._read_reload_token())
        helper = f"""
<script data-preview-reload="true">
(() => {{
  const endpoint = "/__preview/reload-token";
  let currentToken = {reload_token};
  let stopped = false;

  async function poll() {{
    if (stopped) {{
      return;
    }}

    try {{
      const response = await fetch(endpoint, {{ cache: "no-store" }});
      if (response.ok) {{
        const nextToken = (await response.text()).trim();
        if (currentToken && nextToken && nextToken !== currentToken) {{
          window.location.reload();
          return;
        }}
        if (nextToken) {{
          currentToken = nextToken;
        }}
      }}
    }} catch (error) {{
      // Ignore transient preview polling failures and try again.
    }}

    window.setTimeout(poll, 1000);
  }}

  window.addEventListener("beforeunload", () => {{
    stopped = true;
  }}, {{ once: true }});

  window.setTimeout(poll, 1000);
}})();
</script>
"""

        if "</body>" in html_text:
            return html_text.replace("</body>", f"{helper}</body>", 1)

        return f"{html_text}{helper}"

    def _serve_reload_token(self) -> None:
        if not self.reload_token_file:
            self.send_error(404, "Preview auto reload is disabled.")
            return

        payload = f"{self._read_reload_token()}\n".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store, max-age=0, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        if urlsplit(self.path).path == "/__preview/reload-token":
            return

        super().log_message(format, *args)

    def do_HEAD(self) -> None:
        request_path = urlsplit(self.path).path
        if request_path == "/__preview/reload-token":
            self._serve_reload_token()
            return

        super().do_HEAD()

    def do_GET(self) -> None:
        request_path, local_path = self._resolve_local_path()
        if request_path == "/__preview/reload-token":
            self._serve_reload_token()
            return

        if self.reload_token_file and local_path.suffix.lower() == ".html" and local_path.exists():
            payload = self._inject_preview_reload_helper(
                local_path.read_text(encoding="utf-8")
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        super().do_GET()

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
    parser.add_argument("--reload-token-file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handler = functools.partial(
        PreviewRequestHandler,
        directory=args.directory,
        reload_token_file=args.reload_token_file,
    )
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
