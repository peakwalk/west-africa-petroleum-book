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

check_exists() {
  file_path="$1"

  if [ ! -f "$file_path" ]; then
    echo "Missing expected file $file_path" >&2
    exit 1
  fi
}

check_contains public/index.html 'class="landing-shell"'
check_contains public/index.html 'class="hero-panel"'
check_contains public/index.html 'class="chapter-preview-card"'
check_contains public/index.html 'class="site-header-inner"'
check_contains public/index.html 'upstream-atlas-favicon.png?v=2'
check_contains public/index.html 'href="chapters/"'
check_contains public/index.html 'class="current-link" href="/">Home</a>'
check_not_contains public/index.html 'href="book/toc.html"'
check_not_contains public/index.html 'section-heading section-heading-centered'
check_contains public/index.html 'fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:wght@400;500;600;700&display=swap'
check_contains assets/css/landing.css '--page-bg: #ffffff;'
check_contains assets/css/landing.css '--surface-muted: #f1f5f9;'
check_contains assets/css/landing.css 'border-radius: 0.5rem;'
check_contains assets/css/landing.css 'font-weight: 500;'
check_not_contains assets/css/landing.css '@import url("https://fonts.googleapis.com'
check_not_contains scripts/generate-chapters-page.mjs 'replaceAll('

check_exists public/chapters/index.html
check_contains public/chapters/index.html 'Chapter Library'
check_contains public/chapters/index.html 'class="site-header-inner"'
check_contains public/chapters/index.html 'class="current-link" href="./">Chapters</a>'
check_contains public/chapters/index.html '<h2>Part I: General Information on the Oil Industry</h2>'
check_contains public/chapters/index.html 'class="chapter-card-header"'
check_contains public/chapters/index.html 'class="chapter-card-status"'
check_contains public/chapters/index.html 'class="chapter-card-reading"'
check_contains public/chapters/index.html 'data-tooltip="Estimated reading time based on'
check_contains public/chapters/index.html 'Estimated reading time based on'
check_contains public/chapters/index.html 'Additional Resources'
check_not_contains public/chapters/index.html 'Open chapter'
check_not_contains public/chapters/index.html ' entries</p>'
check_not_contains public/chapters/index.html 'title="Estimated reading time based on'
check_contains public/chapters/index.html 'General Information on the Oil Industry'
check_contains public/chapters/index.html '../book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html'
check_contains public/chapters/index.html '../#about'

check_contains public/book/index.html 'book-shell'
check_contains public/book/index.html 'id="book-progress-fill"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="book-outline"'
check_contains public/book/index.html 'upstream-atlas-favicon.png?v=2'
check_contains public/book/index.html 'fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:wght@400;500;600;700&display=swap'
check_not_contains public/book/index.html 'favicon-de23e50b.svg'
check_not_contains public/book/index.html 'favicon-8114d1fc.png'
check_contains theme/custom.css '--paper: #ffffff;'
check_contains theme/custom.css '--sidebar-bg: #f8fafc;'
check_contains theme/custom.css 'font-size: 1rem;'
check_contains theme/custom.css 'background: rgba(255, 255, 255, 0.96);'
check_contains theme/custom.css 'font-weight: 400;'
check_not_contains theme/custom.css '@import url("https://fonts.googleapis.com'

echo "Site render checks passed."
