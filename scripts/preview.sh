#!/usr/bin/env sh
set -eu

HOST="${HOST:-127.0.0.1}"
PORT="${1:-${PORT:-3002}}"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PUBLIC_DIR="$ROOT_DIR/public"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_command mdbook
require_command python3

cd "$ROOT_DIR"

rm -rf "$PUBLIC_DIR"
mkdir -p "$PUBLIC_DIR"

cp "$ROOT_DIR/index.html" "$PUBLIC_DIR/index.html"
cp -R "$ROOT_DIR/assets" "$PUBLIC_DIR/assets"

mdbook build --dest-dir "$PUBLIC_DIR/book"

cat <<EOF

Preview site is ready:
  Landing page: http://$HOST:$PORT/
  mdBook:       http://$HOST:$PORT/book/

Press Ctrl+C to stop the server.

EOF

python3 -m http.server "$PORT" --bind "$HOST" --directory "$PUBLIC_DIR"
