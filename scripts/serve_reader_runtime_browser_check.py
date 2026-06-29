from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port-file", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directory = str(Path(args.directory).resolve())
    port_file = Path(args.port_file)
    handler = partial(SimpleHTTPRequestHandler, directory=directory)

    with ThreadingHTTPServer((args.host, 0), handler) as server:
        port_file.write_text(f"{server.server_port}\n", encoding="utf-8")
        print(
            f"Serving browser runtime check on http://{args.host}:{server.server_port}/ from {directory}",
            flush=True,
        )
        server.serve_forever()


if __name__ == "__main__":
    main()
