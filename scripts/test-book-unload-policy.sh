#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cd "$ROOT_DIR"
npm run build:site >/dev/null

BOOK_JS_PATH="$(find "$ROOT_DIR/public/book" -maxdepth 1 -name 'book-*.js' | head -n 1)"

if [ -z "$BOOK_JS_PATH" ]; then
  echo "Missing generated mdBook core bundle under public/book" >&2
  exit 1
fi

if grep -q 'window.onunload = function() { };' "$BOOK_JS_PATH"; then
  echo "Expected generated mdBook core bundle to omit window.onunload workaround" >&2
  exit 1
fi

echo "Generated mdBook core bundle omits window.onunload."
