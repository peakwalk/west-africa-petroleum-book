#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
SERVER_SCRIPT="$ROOT_DIR/scripts/preview_server.py"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/preview-cache.XXXXXX")"
TOKEN_FILE="$TMP_DIR/reload-token.txt"
PORT="${PORT:-38123}"
HOST="${HOST:-127.0.0.1}"
DISPLAY_HOST="${DISPLAY_HOST:-192.168.0.104}"
SERVER_PID=""

cleanup() {
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

mkdir -p "$TMP_DIR/assets/css"
printf '%s\n' '<!doctype html><html><body>preview</body></html>' > "$TMP_DIR/index.html"
printf '%s\n' 'body { color: #123456; }' > "$TMP_DIR/assets/css/app.css"
printf '%s\n' 'token-alpha' > "$TOKEN_FILE"

python3 "$SERVER_SCRIPT" --host "$HOST" --display-host "$DISPLAY_HOST" --port "$PORT" --directory "$TMP_DIR" --reload-token-file "$TOKEN_FILE" >/tmp/preview-cache-server.log 2>&1 &
SERVER_PID="$!"

for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsSI "http://$HOST:$PORT/index.html" >/tmp/preview-cache-html.headers 2>/dev/null; then
    break
  fi
  sleep 0.2
done

curl -fsSI "http://$HOST:$PORT/index.html" >/tmp/preview-cache-html.headers
curl -fsSI "http://$HOST:$PORT/assets/css/app.css" >/tmp/preview-cache-css.headers
curl -fsS "http://$HOST:$PORT/index.html" >/tmp/preview-cache-html.body
curl -fsS "http://$HOST:$PORT/__preview/reload-token" >/tmp/preview-cache-token.body

grep -qi '^Cache-Control: no-store, max-age=0, must-revalidate' /tmp/preview-cache-html.headers
grep -qi '^Pragma: no-cache' /tmp/preview-cache-html.headers
grep -qi '^Expires: 0' /tmp/preview-cache-html.headers
grep -q 'token-alpha' /tmp/preview-cache-token.body
grep -q 'data-preview-reload' /tmp/preview-cache-html.body
grep -q '/__preview/reload-token' /tmp/preview-cache-html.body

if grep -q 'data-preview-reload' "$TMP_DIR/index.html"; then
  echo "Expected preview HTML injection to stay out of built files on disk" >&2
  exit 1
fi

printf '%s\n' 'token-beta' > "$TOKEN_FILE"
curl -fsS "http://$HOST:$PORT/__preview/reload-token" >/tmp/preview-cache-token.body
grep -q 'token-beta' /tmp/preview-cache-token.body

if grep -qi '^Cache-Control: no-store' /tmp/preview-cache-css.headers; then
  echo "Expected non-HTML preview assets to avoid no-store cache headers" >&2
  exit 1
fi

grep -q "Serving preview on http://$DISPLAY_HOST:$PORT/" /tmp/preview-cache-server.log
grep -q '"GET /index.html HTTP/1.1" 200 -' /tmp/preview-cache-server.log

if grep -q '/__preview/reload-token' /tmp/preview-cache-server.log; then
  echo "Expected preview reload-token polling requests to stay out of the preview server log" >&2
  exit 1
fi

echo "Preview cache header checks passed."
