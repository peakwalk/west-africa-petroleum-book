#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cd "$ROOT_DIR"
npm run build:site >/dev/null

check_contains() {
  file_path="$1"
  pattern="$2"

  if ! grep -q -- "$pattern" "$file_path"; then
    echo "Missing expected pattern '$pattern' in $file_path" >&2
    exit 1
  fi
}

check_not_contains() {
  file_path="$1"
  pattern="$2"

  if grep -q -- "$pattern" "$file_path"; then
    echo "Unexpected pattern '$pattern' found in $file_path" >&2
    exit 1
  fi
}

TARGET="public/book/chapters/glossary.html"

check_contains "$TARGET" 'class="chapter-nav-arrow"'
check_contains "$TARGET" 'class="chapter-nav-badge-shell"'
check_contains "$TARGET" 'class="chapter-nav-badge"'
check_contains "$TARGET" 'class="chapter-nav-label"'
check_contains "$TARGET" 'class="chapter-nav-body"'
check_contains "$TARGET" 'class="chapter-nav-title"'
check_contains "$TARGET" 'class="chapter-nav-dek"'
check_not_contains "$TARGET" 'class="chapter-nav-meta"'
check_not_contains "$TARGET" 'class="chapter-pagination-eyebrow"'
check_not_contains theme/custom.css '.chapter-nav-meta'
check_not_contains theme/custom.css '.chapter-pagination-eyebrow'

check_contains theme/custom.js 'function syncChapterPaginationHeights()'
check_contains theme/custom.js 'function installChapterPaginationMeta()'
check_contains theme/custom.js 'function loadReaderPageMeta()'
check_contains theme/custom.js 'card.dataset.chapterBadgeType = "number";'
check_contains theme/custom.js 'card.style.height = "auto";'
check_contains theme/custom.js 'card.style.height = maxHeight + "px";'

if ! sed -n '/class="chapter-nav-card chapter-nav-previous"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'chapter-nav-badge-shell.*chapter-nav-body'; then
  echo "Expected previous chapter card to render the badge before the body in theme/index.hbs" >&2
  exit 1
fi

if ! sed -n '/class="chapter-nav-card chapter-nav-next"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'chapter-nav-body.*chapter-nav-badge-shell'; then
  echo "Expected next chapter card to render the body before the badge in theme/index.hbs" >&2
  exit 1
fi

DESKTOP_RULES="$(awk '
  /^\.chapter-pagination \{/ {
    in_block = 1
  }

  in_block {
    block = block $0 ORS

    if ($0 ~ /^\.chapter-nav-placeholder \{/ ) {
      placeholder = 1
    } else if (placeholder && $0 ~ /^\}/) {
      printf "%s", block
      exit
    }
  }
' theme/custom.css)"

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: 232px;'; then
  echo "Expected desktop chapter card width to be fixed at 232px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'height: 80px;'; then
  echo "Expected desktop chapter card height to be fixed at 80px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'margin-top: 24px;'; then
  echo "Expected chapter pagination top margin to be 24px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'min-height: 80px;'; then
  echo "Expected desktop chapter card minimum height to remain 80px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'padding: 10px 12px;'; then
  echo "Expected desktop chapter card padding to match the compact rounded card sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'box-sizing: border-box;'; then
  echo "Expected chapter cards to use border-box sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'overflow: hidden;'; then
  echo "Expected desktop chapter cards to clip decorative layers in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'gap: 12px;'; then
  echo "Expected desktop chapter pagination gap to be fixed at 12px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: 42px;'; then
  echo "Expected desktop chapter badge sizing to remain explicit in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'text-align: right;'; then
  echo "Expected desktop next chapter text to be right-aligned in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q -- '-webkit-line-clamp: 2;'; then
  echo "Expected desktop chapter card dek copy to clamp to two lines in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'mask: url("data:image/svg+xml,'; then
  echo "Expected desktop chapter cards to include the inline SVG rig ornament in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'transform: translateY(-1px);'; then
  echo "Expected chapter card hover to avoid vertical movement in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'transform: translateX('; then
  echo "Expected chapter arrow hover to avoid horizontal movement in theme/custom.css" >&2
  exit 1
fi

NARROW_RULES="$(awk '
  /@media \(max-width: 760px\)/ {
    in_media = 1
    block = $0 ORS
    next
  }

  in_media {
    block = block $0 ORS

    if ($0 ~ /@media \(max-width: 900px\)/) {
      last_block = block
      in_media = 0
    }
  }

  END {
    printf "%s", last_block
  }
' theme/custom.css)"

if ! printf '%s' "$NARROW_RULES" | grep -q 'flex-direction: column;'; then
  echo "Expected narrow-screen chapter pagination to stack vertically in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'align-items: stretch;'; then
  echo "Expected narrow-screen chapter pagination to stretch stacked cards in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'width: 100%;'; then
  echo "Expected stacked narrow-screen chapter cards to span the reader column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'align-self: stretch;'; then
  echo "Expected narrow-screen chapter cards to stretch evenly in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'min-height: 80px;'; then
  echo "Expected stacked narrow-screen chapter cards to keep the 80px minimum height in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'padding: 0.75rem 0.9rem;'; then
  echo "Expected stacked narrow-screen chapter card padding to match the redesign in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'font-size: 1rem;'; then
  echo "Expected stacked narrow-screen chapter title sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'justify-items: end;'; then
  echo "Expected narrow-screen next chapter body to right-align its text in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'justify-self: end;'; then
  echo "Expected narrow-screen next chapter label to right-align in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q -- '-webkit-line-clamp: 2;'; then
  echo "Expected narrow-screen chapter card dek copy to clamp to two lines in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'display: none;'; then
  echo "Expected narrow-screen chapter pagination placeholder to be hidden in theme/custom.css" >&2
  exit 1
fi
