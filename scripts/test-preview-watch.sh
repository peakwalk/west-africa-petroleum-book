#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
WATCH_SCRIPT="$ROOT_DIR/scripts/preview_watch.mjs"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/preview-watch.XXXXXX")"
SRC_DIR="$TMP_DIR/src"
OUT_DIR="$TMP_DIR/out"
TOKEN_FILE="$TMP_DIR/reload-token.txt"
COUNT_FILE="$TMP_DIR/build-count.txt"
LOCK_FILE="$TMP_DIR/build.lock"
BUILD_SCRIPT="$TMP_DIR/build.sh"
WATCH_PID=""

cleanup() {
  if [ -n "$WATCH_PID" ] && kill -0 "$WATCH_PID" 2>/dev/null; then
    kill "$WATCH_PID" >/dev/null 2>&1 || true
    wait "$WATCH_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

mkdir -p "$SRC_DIR" "$OUT_DIR"
printf '%s' 'zero' > "$SRC_DIR/input.txt"

cat >"$BUILD_SCRIPT" <<EOF
#!/usr/bin/env sh
set -eu
if [ -e "$LOCK_FILE" ]; then
  echo "Concurrent build detected" >&2
  exit 1
fi
trap 'rm -f "$LOCK_FILE"' EXIT INT TERM
: > "$LOCK_FILE"
count=0
if [ -f "$COUNT_FILE" ]; then
  count="\$(cat "$COUNT_FILE")"
fi
count=\$((count + 1))
printf '%s\n' "\$count" > "$COUNT_FILE"
snapshot="\$(cat "$SRC_DIR/input.txt")"
sleep 0.4
printf '%s' "\$snapshot" > "$OUT_DIR/output.txt"
EOF
chmod +x "$BUILD_SCRIPT"

node "$WATCH_SCRIPT" --scan-ms 50 --debounce-ms 100 --reload-token-file "$TOKEN_FILE" --watch-path "$SRC_DIR" -- "$BUILD_SCRIPT" >/tmp/preview-watch.log 2>&1 &
WATCH_PID="$!"

for _ in 1 2 3 4 5 6 7 8 9 10; do
  if [ -f "$TOKEN_FILE" ]; then
    break
  fi
  sleep 0.1
done

INITIAL_TOKEN="$(cat "$TOKEN_FILE")"

printf '%s' 'one' > "$SRC_DIR/input.txt"
sleep 0.25
printf '%s' 'two' > "$SRC_DIR/input.txt"

for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if [ -f "$COUNT_FILE" ] && [ "$(cat "$COUNT_FILE")" -ge 2 ] && [ -f "$OUT_DIR/output.txt" ] && [ "$(cat "$OUT_DIR/output.txt")" = "two" ]; then
    break
  fi
  sleep 0.1
done

if [ ! -f "$COUNT_FILE" ]; then
  echo "Expected preview watch build count file to be created" >&2
  exit 1
fi

if [ "$(cat "$COUNT_FILE")" -lt 2 ]; then
  echo "Expected preview watcher to queue a follow-up rebuild after a second change" >&2
  exit 1
fi

if [ ! -f "$OUT_DIR/output.txt" ] || [ "$(cat "$OUT_DIR/output.txt")" != "two" ]; then
  echo "Expected preview watcher output to match the latest source content" >&2
  exit 1
fi

UPDATED_TOKEN="$(cat "$TOKEN_FILE")"
if [ "$INITIAL_TOKEN" = "$UPDATED_TOKEN" ]; then
  echo "Expected preview watcher to advance the reload token after a successful rebuild" >&2
  exit 1
fi

echo "Preview watch rebuild checks passed."
