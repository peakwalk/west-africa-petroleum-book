#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/preview-build.XXXXXX")"
TMP_BIN_DIR="$TMP_DIR/bin"
REAL_PYTHON3="$(command -v python3)"

cleanup() {
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR"

mkdir -p "$TMP_BIN_DIR"

cat >"$TMP_BIN_DIR/python3" <<EOF
#!/usr/bin/env sh
if [ "\${1:-}" = "$ROOT_DIR/scripts/preview_server.py" ]; then
  exit 0
fi
exec "$REAL_PYTHON3" "\$@"
EOF
chmod +x "$TMP_BIN_DIR/python3"

PATH="$TMP_BIN_DIR:$PATH" "$ROOT_DIR/scripts/preview.sh" >/tmp/preview-build.log 2>&1

test -f "$ROOT_DIR/public/book/reader-page-meta.json"
grep -q 'chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html' "$ROOT_DIR/public/book/reader-page-meta.json"

echo "Preview build includes reader page metadata."
