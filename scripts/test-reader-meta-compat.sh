#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
BOOK_DIR="$ROOT_DIR/public/book"
INDEX_PATH="$BOOK_DIR/index.html"
BACKUP_PATH=""
RESTORE_MODE="delete"

cleanup() {
  if [ -n "$BACKUP_PATH" ] && [ -f "$BACKUP_PATH" ]; then
    mv "$BACKUP_PATH" "$INDEX_PATH"
    return
  fi

  if [ "$RESTORE_MODE" = "delete" ]; then
    rm -f "$INDEX_PATH"
  fi
}

trap cleanup EXIT INT TERM

mkdir -p "$BOOK_DIR"

if [ -f "$INDEX_PATH" ]; then
  BACKUP_PATH="$(mktemp "${TMPDIR:-/tmp}/reader-meta-index.XXXXXX")"
  cp "$INDEX_PATH" "$BACKUP_PATH"
else
  RESTORE_MODE="delete"
fi

cat >"$INDEX_PATH" <<'EOF'
<!doctype html>
<html>
  <body>
    <img src="../images/example.png" alt="">
    <a href="../chapters/example.html">Example chapter</a>
  </body>
</html>
EOF

node --input-type=module -e "String.prototype.replaceAll = undefined; await import('./scripts/build_reader_page_meta.mjs');"

grep -q 'src="images/example.png"' "$INDEX_PATH"
grep -q 'href="chapters/example.html"' "$INDEX_PATH"

echo "Reader metadata builder stays compatible without String.prototype.replaceAll."
