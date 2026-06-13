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
check_contains theme/custom.js 'card.dataset.chapterNavHasDek = dekText ? "true" : "false";'
check_contains theme/custom.js 'requestAnimationFrame(syncChapterPaginationHeights);'
check_contains theme/custom.js 'window.matchMedia("(min-width: 761px)")'
check_contains theme/custom.js 'card.style.height = "auto";'
check_contains theme/custom.js 'card.style.height = "";'
check_contains theme/custom.js 'card.style.height = maxHeight + "px";'

if ! sed -n '/class="chapter-nav-card chapter-nav-previous"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'chapter-nav-badge-shell.*chapter-nav-body'; then
  echo "Expected previous chapter card to render the badge before the body in theme/index.hbs" >&2
  exit 1
fi

if ! sed -n '/class="chapter-nav-card chapter-nav-previous"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'data-chapter-nav-has-dek="false"'; then
  echo "Expected previous chapter card to declare a no-dek initial state in theme/index.hbs" >&2
  exit 1
fi

if ! sed -n '/class="chapter-nav-card chapter-nav-next"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'chapter-nav-body.*chapter-nav-badge-shell'; then
  echo "Expected next chapter card to render the body before the badge in theme/index.hbs" >&2
  exit 1
fi

if ! sed -n '/class="chapter-nav-card chapter-nav-next"/,/<\/a>/p' theme/index.hbs | tr '\n' ' ' | grep -q 'data-chapter-nav-has-dek="false"'; then
  echo "Expected next chapter card to declare a no-dek initial state in theme/index.hbs" >&2
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

BODY_RULES="$(awk '
  /^\.chapter-nav-body \{/ {
    in_block = 1
  }

  in_block {
    block = block $0 ORS

    if ($0 ~ /^\}/) {
      printf "%s", block
      exit
    }
  }
' theme/custom.css)"

DEK_RULES="$(awk '
  /^\.chapter-nav-dek \{/ {
    in_block = 1
  }

  in_block {
    block = block $0 ORS

    if ($0 ~ /^\}/) {
      printf "%s", block
      exit
    }
  }
' theme/custom.css)"

NO_DEK_TITLE_RULES="$(awk '
  /^\.chapter-nav-card\[data-chapter-nav-has-dek="false"\] \.chapter-nav-title \{/ {
    in_block = 1
  }

  in_block {
    block = block $0 ORS

    if ($0 ~ /^\}/) {
      printf "%s", block
      exit
    }
  }
' theme/custom.css)"

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'display: grid;'; then
  echo "Expected desktop chapter pagination to use a grid layout in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: min(100%, var(--reader-article-body-width));'; then
  echo "Expected desktop chapter pagination container width to match the reader body width in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'grid-template-columns: repeat(2, minmax(0, 1fr));'; then
  echo "Expected desktop chapter pagination to split into two equal columns in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'justify-content: space-between;'; then
  echo "Expected desktop chapter pagination to stop using space-between in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: 100%;'; then
  echo "Expected desktop chapter cards to fill their grid columns in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'max-width: none;'; then
  echo "Expected desktop chapter cards to remove the 224px cap in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'margin-top: 24px;'; then
  echo "Expected chapter pagination top margin to be 24px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'min-height: 92px;'; then
  echo "Expected desktop chapter card minimum height to increase to 92px in theme/custom.css" >&2
  exit 1
fi

if printf '%s\n' "$DESKTOP_RULES" | grep -q '^  height: 80px;$'; then
  echo "Expected desktop chapter cards to stop using the fixed 80px height in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'padding: 12px;'; then
  echo "Expected desktop chapter card padding to be 12px on all sides in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'border-radius: 12px;'; then
  echo "Expected desktop chapter card corner radius to be 12px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'background: var(--reader-table-card-bg);'; then
  echo "Expected desktop chapter cards to reuse the table/image card background token in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'radial-gradient('; then
  echo "Expected desktop chapter cards to stop using radial background gradients in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'linear-gradient('; then
  echo "Expected desktop chapter cards to stop using linear background gradients in theme/custom.css" >&2
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

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: 44px;'; then
  echo "Expected desktop chapter badge width to be 44px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'height: 44px;'; then
  echo "Expected desktop chapter badge height to be 44px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'box-sizing: border-box;'; then
  echo "Expected desktop chapter badge to use border-box sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'aspect-ratio: 1 / 1;'; then
  echo "Expected desktop chapter badge to lock a 1:1 aspect ratio in theme/custom.css" >&2
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

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'font-size: 16px;'; then
  echo "Expected desktop chapter title sizing to increase to 16px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'font-size: 10px;'; then
  echo "Expected desktop chapter dek sizing to be 10px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'prototype-hero-graywhite-left.png'; then
  echo "Expected desktop previous chapter card to use prototype-hero-graywhite-left.png in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'prototype-hero-graywhite-right.png'; then
  echo "Expected desktop next chapter card to use prototype-hero-graywhite-right.png in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q -- '--chapter-nav-ornament-column: 116px;'; then
  echo "Expected desktop chapter cards to reserve a 116px ornament column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'width: var(--chapter-nav-ornament-width);'; then
  echo "Expected desktop chapter card overlay width to be driven by a dedicated ornament sizing variable in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q -- '--chapter-nav-ornament-width: 116px;'; then
  echo "Expected desktop chapter card overlay width token to be 116px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q -- '--chapter-nav-ornament-height: 80px;'; then
  echo "Expected desktop chapter card overlay height token to be 80px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'bottom: 8px;'; then
  echo "Expected desktop chapter card overlay to anchor 8px above the bottom edge in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'margin-block: auto;'; then
  echo "Expected desktop chapter card overlay to stop centering vertically once the edge gutter is reserved in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'background-position: right bottom;'; then
  echo "Expected desktop previous chapter ornament to anchor at the right bottom edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'right: 0;'; then
  echo "Expected desktop previous chapter ornament to sit flush against the right edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'background-position: left bottom;'; then
  echo "Expected desktop next chapter ornament to anchor at the left bottom edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'left: 0;'; then
  echo "Expected desktop next chapter ornament to sit flush against the left edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'background-size: contain;'; then
  echo "Expected desktop chapter cards to render the decorative overlay with contain sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'opacity: 0.3;'; then
  echo "Expected desktop chapter card decorative overlay opacity to be 0.3 in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'mix-blend-mode:'; then
  echo "Expected desktop chapter card decorative overlay to rely on precomposed transparency instead of runtime blending in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'grid-template-columns: 44px minmax(0, 1fr) var(--chapter-nav-ornament-column);'; then
  echo "Expected desktop previous chapter card to reserve a trailing ornament column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'grid-template-columns: var(--chapter-nav-ornament-column) minmax(0, 1fr) 44px;'; then
  echo "Expected desktop next chapter card to reserve a leading ornament column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DESKTOP_RULES" | grep -q 'grid-column: 2;'; then
  echo "Expected desktop chapter body to be pinned to the center grid column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$BODY_RULES" | grep -q 'display: flex;'; then
  echo "Expected chapter body to use a column flex layout so text can pin to the bottom edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$BODY_RULES" | grep -q 'flex-direction: column;'; then
  echo "Expected chapter body to stack label, title, and dek vertically in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$BODY_RULES" | grep -q 'align-self: stretch;'; then
  echo "Expected chapter body to stretch to the card height in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$BODY_RULES" | grep -q 'align-content: center;'; then
  echo "Expected chapter body to stop vertically centering its text in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$DEK_RULES" | grep -q 'margin-top: auto;'; then
  echo "Expected chapter dek text to push itself to the card bottom in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NO_DEK_TITLE_RULES" | grep -q 'margin-top: auto;'; then
  echo "Expected chapter title to fall back to the card bottom when no dek is available in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'background-blend-mode:'; then
  echo "Expected desktop chapter cards to avoid runtime background blending once the overlay asset is precomposed in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'mask-image:'; then
  echo "Expected desktop chapter cards to avoid CSS masking once the ornament asset has transparent edges in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'filter: grayscale('; then
  echo "Expected desktop chapter cards to avoid runtime grayscale filtering once the overlay asset is precomposed in theme/custom.css" >&2
  exit 1
fi

if printf '%s' "$DESKTOP_RULES" | grep -q 'mix-blend-mode: screen;'; then
  echo "Expected desktop chapter cards to avoid screen blending for the decorative overlay in theme/custom.css" >&2
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

if ! printf '%s' "$NARROW_RULES" | grep -q 'gap: 12px;'; then
  echo "Expected narrow-screen chapter pagination gap to be 12px in theme/custom.css" >&2
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

if ! printf '%s' "$NARROW_RULES" | grep -q 'min-height: 92px;'; then
  echo "Expected stacked narrow-screen chapter cards to use the 92px minimum height in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'padding: 12px;'; then
  echo "Expected stacked narrow-screen chapter card padding to be 12px on all sides in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'grid-template-columns: 44px minmax(0, 1fr) 104px;'; then
  echo "Expected narrow-screen previous chapter card to reserve a trailing ornament column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'grid-template-columns: 104px minmax(0, 1fr) 44px;'; then
  echo "Expected narrow-screen next chapter card to reserve a leading ornament column in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'font-size: 16px;'; then
  echo "Expected stacked narrow-screen chapter title sizing in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'justify-items: end;'; then
  echo "Expected narrow-screen next chapter body to right-align its text in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'text-align: right;'; then
  echo "Expected narrow-screen next chapter body text to be right-aligned in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'justify-self: end;'; then
  echo "Expected narrow-screen next chapter label to right-align in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'text-align: left;'; then
  echo "Expected narrow-screen previous chapter body text to remain left-aligned in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q -- '-webkit-line-clamp: 2;'; then
  echo "Expected narrow-screen chapter card dek copy to clamp to two lines in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'width: 44px;'; then
  echo "Expected narrow-screen chapter badge width to be 44px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'height: 44px;'; then
  echo "Expected narrow-screen chapter badge height to be 44px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'font-size: 10px;'; then
  echo "Expected narrow-screen chapter dek sizing to be 10px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'width: 104px;'; then
  echo "Expected narrow-screen chapter ornament width to be 104px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q -- '--chapter-nav-ornament-height: 80px;'; then
  echo "Expected narrow-screen chapter ornament height token to be 80px in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'bottom: 8px;'; then
  echo "Expected narrow-screen chapter ornament to sit 8px above the bottom edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'opacity: 0.3;'; then
  echo "Expected narrow-screen chapter ornament opacity to be 0.3 in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'right: 0;'; then
  echo "Expected narrow-screen previous chapter ornament to sit flush against the right edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'left: 0;'; then
  echo "Expected narrow-screen next chapter ornament to sit flush against the left edge in theme/custom.css" >&2
  exit 1
fi

if ! printf '%s' "$NARROW_RULES" | grep -q 'display: none;'; then
  echo "Expected narrow-screen chapter pagination placeholder to be hidden in theme/custom.css" >&2
  exit 1
fi
