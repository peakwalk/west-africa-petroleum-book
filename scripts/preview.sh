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

require_command python3

cd "$ROOT_DIR"

npm run build:site >/dev/null

cat <<EOF

Preview site is ready:
  Landing page: http://$HOST:$PORT/
  mdBook:       http://$HOST:$PORT/book/
  French site:  http://$HOST:$PORT/fr/
  French book:  http://$HOST:$PORT/fr/book/

Press Ctrl+C to stop the server.

EOF

python3 "$ROOT_DIR/scripts/preview_server.py" --host "$HOST" --port "$PORT" --directory "$PUBLIC_DIR"
