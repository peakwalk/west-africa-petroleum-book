#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cd "$ROOT_DIR"
npm run build:site >/dev/null

run_docx_formula_check_if_available() {
  edition="$1"
  docx_path="$(
    python3 - "$edition" <<'PY'
import sys
from scripts.edition_config import get_edition

print(get_edition(sys.argv[1]).docx_path)
PY
  )"

  if [ -f "$docx_path" ]; then
    python3 scripts/check_docx_formula_coverage.py --edition "$edition" >/dev/null
  else
    echo "Skipping DOCX formula coverage check for $edition; missing $docx_path" >&2
  fi
}

create_temp_file() {
  file_prefix="$1"
  file_suffix="$2"

  python3 - "$file_prefix" "$file_suffix" <<'PY'
import os
import sys
import tempfile

prefix = sys.argv[1]
suffix = sys.argv[2]
tmp_dir = os.environ.get("TMPDIR") or "/tmp"
fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=tmp_dir)
os.close(fd)
print(temp_path)
PY
}

run_browser_runtime_check_if_available() {
  if [ "$(uname -s)" = "Darwin" ] && command -v swift >/dev/null 2>&1; then
    browser_page_config="$(create_temp_file "reader-runtime-browser-config." ".json")"
    browser_check_scope="${READER_RUNTIME_BROWSER_CHECK_SCOPE:-smoke}"
    browser_server_log="$(create_temp_file "reader-runtime-browser-http." ".log")"
    browser_server_port_file="$(create_temp_file "reader-runtime-browser-port." ".txt")"

    node scripts/build_reader_runtime_browser_check_config.mjs >"$browser_page_config"

    python3 scripts/serve_reader_runtime_browser_check.py \
      --directory public \
      --host 127.0.0.1 \
      --port-file "$browser_server_port_file" >"$browser_server_log" 2>&1 &
    browser_server_pid="$!"

    cleanup_browser_runtime_server() {
      kill "$browser_server_pid" 2>/dev/null || true
      wait "$browser_server_pid" 2>/dev/null || true
      rm -f "$browser_page_config" "$browser_server_log" "$browser_server_port_file"
    }

    trap cleanup_browser_runtime_server EXIT INT TERM
    python3 - "$browser_server_port_file" <<'PY'
from pathlib import Path
import socket
import sys
import time

port_file = Path(sys.argv[1])
deadline = time.time() + 5

while time.time() < deadline:
    try:
        port = int(port_file.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        time.sleep(0.05)
        continue

    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            sys.exit(0)
    except OSError:
        time.sleep(0.05)

print(f"Timed out waiting for local browser check server from {port_file}", file=sys.stderr)
sys.exit(1)
PY
    browser_port="$(cat "$browser_server_port_file")"
    SWIFT_MODULECACHE_PATH="${TMPDIR:-/tmp}/swift-module-cache" \
      CLANG_MODULE_CACHE_PATH="${TMPDIR:-/tmp}/clang-module-cache" \
      swift scripts/check_reader_runtime_browser.swift \
        --base-url "http://127.0.0.1:$browser_port" \
        --scope "$browser_check_scope" \
        --page-config "$browser_page_config" >/dev/null
    trap - EXIT INT TERM
    cleanup_browser_runtime_server
  else
    echo "Skipping browser runtime DOM check; requires macOS swift/WebKit" >&2
  fi
}

run_docx_formula_check_if_available en
run_docx_formula_check_if_available fr

check_contains() {
  file_path="$1"
  pattern="$2"

  if ! grep -Fq -- "$pattern" "$file_path"; then
    echo "Missing expected pattern '$pattern' in $file_path" >&2
    exit 1
  fi
}

check_not_contains() {
  file_path="$1"
  pattern="$2"

  if grep -Fq -- "$pattern" "$file_path"; then
    echo "Unexpected pattern '$pattern' found in $file_path" >&2
    exit 1
  fi
}

check_tree_not_contains() {
  tree_path="$1"
  pattern="$2"

  if rg -Fq -- "$pattern" "$tree_path"; then
    echo "Unexpected pattern '$pattern' found under $tree_path" >&2
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

check_not_exists() {
  file_path="$1"

  if [ -e "$file_path" ]; then
    echo "Unexpected file present at $file_path" >&2
    exit 1
  fi
}

check_file_size_at_most() {
  file_path="$1"
  max_bytes="$2"
  size_bytes="$(wc -c < "$file_path" | tr -d ' ')"

  if [ "$size_bytes" -gt "$max_bytes" ]; then
    echo "Expected $file_path to be <= $max_bytes bytes but was $size_bytes bytes" >&2
    exit 1
  fi
}

check_line_count_at_most() {
  file_path="$1"
  max_lines="$2"
  line_count="$(wc -l < "$file_path" | tr -d ' ')"

  if [ "$line_count" -gt "$max_lines" ]; then
    echo "Expected $file_path to be <= $max_lines lines but was $line_count lines" >&2
    exit 1
  fi
}

check_file_size_at_least() {
  file_path="$1"
  min_bytes="$2"
  size_bytes="$(wc -c < "$file_path" | tr -d ' ')"

  if [ "$size_bytes" -lt "$min_bytes" ]; then
    echo "Expected $file_path to be >= $min_bytes bytes but was $size_bytes bytes" >&2
    exit 1
  fi
}

check_image_has_no_opaque_white_fringe() {
  file_path="$1"
  max_pixels="$2"

  if ! command -v magick >/dev/null 2>&1; then
    return 0
  fi

  fringe_pixels="$(magick "$file_path" -crop 430x110+170+25 +repage -format '%[fx:mean*w*h]' -channel RGBA -fx '(a>0.05 && r>0.92 && g>0.92 && b>0.92)?1:0' info: | cut -d. -f1)"

  if [ "$fringe_pixels" -gt "$max_pixels" ]; then
    echo "Expected $file_path to have <= $max_pixels opaque white pixels but found $fringe_pixels" >&2
    exit 1
  fi
}

build_expanded_landing_css_check_file() {
  output_path="$1"

  python3 - "$output_path" <<'PY'
from pathlib import Path
import re
import sys

output_path = Path(sys.argv[1])
entry_path = Path("assets/css/landing.css").resolve()
import_pattern = re.compile(r'@import\s+"([^"]+)";\s*$')

def expand(path, stack):
    resolved = path.resolve()
    if resolved in stack:
        raise SystemExit(f"Recursive landing CSS import detected: {resolved}")

    stack = (*stack, resolved)
    expanded = []

    for raw_line in resolved.read_text(encoding="utf-8").splitlines(keepends=True):
        match = import_pattern.fullmatch(raw_line.strip())
        if match:
            expanded.append(expand(resolved.parent / match.group(1), stack))
        else:
            expanded.append(raw_line)

    return "".join(expanded)

output_path.write_text(expand(entry_path, ()), encoding="utf-8")
PY
}

check_order() {
  file_path="$1"
  first_pattern="$2"
  second_pattern="$3"
  first_offset="$(LC_ALL=C grep -Fbo -- "$first_pattern" "$file_path" | head -n 1 | cut -d: -f1 || true)"
  second_offset="$(LC_ALL=C grep -Fbo -- "$second_pattern" "$file_path" | head -n 1 | cut -d: -f1 || true)"

  if [ -z "$first_offset" ] || [ -z "$second_offset" ]; then
    echo "Missing expected ordered patterns '$first_pattern' or '$second_pattern' in $file_path" >&2
    exit 1
  fi

  if [ "$first_offset" -ge "$second_offset" ]; then
    echo "Expected '$first_pattern' to appear before '$second_pattern' in $file_path" >&2
    exit 1
  fi
}

check_exists scripts/generate-index-page.mjs
check_exists scripts/generate-legal-pages.mjs
check_exists scripts/shared/landing-shell.mjs
check_exists editions/en/source/images/figure-000.png
check_exists editions/en/content/images/figure-001.webp
check_exists editions/en/content/images/figure-003.webp
check_exists editions/en/content/images/figure-004.webp
check_exists editions/en/content/images/figure-005.webp
check_exists editions/en/content/images/figure-006.webp
check_exists editions/en/content/images/figure-007.webp
check_exists editions/en/content/images/figure-008.webp
check_exists editions/en/content/images/figure-009.webp
check_exists editions/en/content/images/figure-010.webp
check_exists editions/en/content/images/figure-011.webp
check_file_size_at_least editions/en/content/images/figure-011.webp 1
check_exists editions/en/content/images/figure-012.webp
check_exists editions/en/content/images/figure-013.webp
check_exists editions/en/content/images/figure-014.webp
check_exists editions/en/content/images/figure-015.webp
check_exists editions/en/content/images/figure-018.webp
check_exists editions/en/content/images/figure-019.webp
check_exists editions/en/content/images/figure-020.webp
check_exists editions/en/content/images/figure-017.webp
check_exists editions/en/content/images/figure-021.webp
check_exists editions/en/content/images/figure-022.webp
check_exists editions/en/content/images/figure-023.webp
check_exists editions/en/content/images/figure-026.webp
check_exists editions/en/content/images/figure-030.webp
check_exists editions/fr/source/images/figure-000.png
check_exists editions/fr/content/images/figure-001.webp
check_exists editions/fr/content/images/figure-003.webp
check_exists editions/fr/content/images/figure-004.webp
check_exists editions/fr/content/images/figure-005.webp
check_exists editions/fr/content/images/figure-006.webp
check_exists editions/fr/content/images/figure-008.webp
check_exists editions/fr/content/images/figure-009.webp
check_exists editions/fr/content/images/figure-010.webp
check_exists editions/fr/content/images/figure-011.webp
check_exists editions/fr/content/images/figure-012.webp
check_exists editions/fr/content/images/figure-013.webp
check_exists editions/fr/content/images/figure-014.webp
check_exists editions/fr/content/images/figure-015.webp
check_exists editions/fr/content/images/figure-018.webp
check_not_exists editions/en/content/images/figures.zip
check_not_exists editions/en/content/images/figure-000.png
check_not_exists editions/en/content/images/figure-003-trimmed.png
check_not_exists editions/en/content/images/figure-003-trimmed.webp
check_not_exists editions/en/content/images/figure-007-b.webp
check_not_exists editions/fr/content/images/figure-003-trimmed.png
check_not_exists editions/fr/content/images/figure-003-trimmed.webp
check_not_exists editions/fr/content/images/figure-000.png
for file in figure-001.png figure-005.png figure-021.png figure-022.png figure-026.png figure-030.png figure-032.png; do
  check_exists "editions/en/content/images/$file"
done
for file in figure-002.png figure-003.png figure-004.png figure-005.png figure-006.png figure-007.png figure-008.png figure-009.png figure-010.png figure-011.png figure-012.png figure-013.png figure-014.png figure-015.png figure-016.png figure-017.png figure-019.png figure-020.png figure-021.png figure-022.png figure-023.png figure-024.png figure-025.png figure-027.png figure-028.png figure-029.png figure-031.png figure-032.png; do
  check_not_exists "editions/fr/content/images/$file"
done
for file in figure-003.jpg figure-005.jpg figure-009.jpg figure-010.jpg figure-016-a.jpg figure-016-b.jpg figure-024.svg figure-025.svg figure-027.svg figure-028.svg figure-029.svg figure-031.svg figure-032.svg; do
  check_not_exists "editions/en/content/images/$file"
done
for file in figure-017.jpg figure-017.svg figure-018.jpg figure-019.svg figure-023.svg; do
  check_not_exists "editions/en/content/images/$file"
done
for file in figure-002.webp figure-003.jpg figure-005.jpg figure-009.jpg figure-010.jpg figure-016-a.jpg figure-016-b.jpg figure-016.webp figure-018.jpg figure-022.svg figure-024.svg figure-025.svg figure-027.svg figure-028.svg figure-029.svg figure-031.svg figure-032.svg; do
  check_not_exists "editions/fr/content/images/$file"
done
check_exists editions/en/content/images/figure-024.webp
check_exists editions/en/content/images/figure-025.webp
check_exists editions/en/content/images/figure-027.webp
check_exists editions/en/content/images/figure-028.webp
check_exists editions/en/content/images/figure-029.webp
check_exists editions/en/content/images/figure-031.webp
check_exists editions/en/content/images/figure-032.webp
check_exists editions/en/content/images/figure-000.webp
check_exists assets/images/west-africa-intelligence-overlay.svg
check_exists assets/images/upstream-atlas-nav-logo.webp
check_exists assets/images/upstream-atlas-hero-v7-clean-left.webp
check_exists assets/images/prototype-hero-graywhite-left.webp
check_exists assets/images/prototype-hero-graywhite-right.webp
check_exists assets/icons/homepage/icon-research.svg
check_exists assets/icons/homepage/icon-industry-monitoring.svg
check_exists assets/icons/homepage/icon-intelligence.svg
check_exists assets/icons/homepage/icon-start-reading.svg
check_exists assets/icons/homepage/icon-menu.svg
check_exists assets/icons/homepage/icon-close.svg
check_exists assets/icons/homepage/icon-production.svg
check_exists assets/icons/homepage/icon-exploration.svg
check_exists assets/icons/homepage/icon-fiscal.svg
check_exists assets/icons/homepage/icon-regulation.svg
check_exists assets/icons/homepage-cropped/icon-research.webp
check_exists assets/icons/homepage-cropped/icon-industry-monitoring.webp
check_exists assets/icons/homepage-cropped/icon-intelligence.webp
check_exists assets/icons/homepage-cropped/icon-production.webp
check_exists assets/icons/homepage-cropped/icon-exploration.webp
check_exists assets/icons/homepage-cropped/icon-fiscal.webp
check_exists assets/icons/homepage-cropped/icon-regulation.webp
check_exists assets/icons/homepage-cropped/icon-audience-research.webp
check_exists assets/icons/homepage-cropped/icon-audience-policy.webp
check_exists assets/icons/homepage-cropped/icon-audience-operators.webp
check_exists assets/icons/homepage/icon-audience-research.svg
check_exists assets/icons/homepage/icon-audience-policy.svg
check_exists assets/icons/homepage/icon-audience-operators.svg
check_exists assets/icons/homepage-sprite.svg
check_exists assets/icons/stakeholders/governments.png
check_exists assets/icons/stakeholders/regulators.png
check_exists assets/icons/stakeholders/national-oil-companies.png
check_exists assets/icons/stakeholders/operators.png
check_exists assets/icons/stakeholders/investors.png
check_exists assets/icons/stakeholders/universities-researchers.png
check_exists scripts/build_reader_page_meta.mjs
check_exists scripts/check_reader_runtime_build_contract.mjs
check_exists scripts/check_reader_runtime_outline.mjs
check_exists scripts/check_reader_runtime_browser.swift
check_contains package.json '"build:index": "node scripts/generate-index-page.mjs"'
check_contains package.json '"build:legal": "node scripts/generate-legal-pages.mjs"'
check_contains package.json '"build:reader-meta": "node scripts/build_reader_page_meta.mjs"'
check_contains package.json '"build:site": "node scripts/build_site.mjs"'
check_contains .github/workflows/pages.yml 'run: npm run test:site'
check_not_contains .github/workflows/pages.yml 'cp index.html public/index.html'
check_contains scripts/generate-index-page.mjs 'renderLandingHead'
check_contains scripts/generate-index-page.mjs 'renderLandingHeader'
check_contains scripts/generate-index-page.mjs 'renderLandingFooter'
check_contains scripts/generate-chapters-page.mjs 'from "./shared/landing-shell.mjs"'
check_contains scripts/generate-chapters-page.mjs 'renderLandingHead'
check_contains scripts/generate-chapters-page.mjs 'renderLandingHeader'
check_contains scripts/generate-chapters-page.mjs 'renderLandingFooter'
check_contains scripts/build_reader_page_meta.mjs '"log", "-1"'
check_contains scripts/build_reader_page_meta.mjs 'reader-page-meta.json'
check_contains scripts/shared/landing-shell.mjs 'function renderLandingHead'
check_contains scripts/shared/landing-shell.mjs 'function renderLandingHeader'
check_contains scripts/shared/landing-shell.mjs 'function renderLandingFooter'
check_not_contains editions/en/book.toml 'git-repository-url = "https://github.com/peakwalk/west-africa-petroleum-book"'
check_not_contains editions/en/book.toml 'edit-url-template = "https://github.com/peakwalk/west-africa-petroleum-book/edit/main/{path}"'
check_not_contains editions/fr/book.toml 'git-repository-url = "https://github.com/peakwalk/west-africa-petroleum-book"'
check_not_contains editions/fr/book.toml 'edit-url-template = "https://github.com/peakwalk/west-africa-petroleum-book/edit/main/{path}"'

check_contains public/index.html 'class="landing-shell"'
check_contains public/index.html 'class="hero-panel hero-panel-v2"'
check_contains public/index.html 'class="hero-copy-block hero-copy-block-v2"'
check_contains public/index.html 'class="site-header-inner"'
check_contains public/index.html 'assets/css/landing.css?v=20260703'
check_contains public/index.html 'upstream-atlas-favicon.png?v=2'
check_contains public/index.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/index.html 'upstream-atlas-nav-logo.png'
check_contains public/index.html 'upstream-atlas-icon.png'
check_contains public/index.html 'href="/chapters/"'
check_contains public/index.html 'class="current-link" href="/">Home</a>'
check_contains public/index.html 'href="/#countries">Countries</a>'
check_contains public/index.html 'href="/#topics">Chapters</a>'
check_contains public/index.html 'href="/#search">Search</a>'
check_not_contains public/index.html 'href="/#about">About</a>'
check_not_contains public/index.html 'href="/#resources">Resources</a>'
check_contains public/index.html 'mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas%20Enquiry'
check_not_contains public/index.html 'class="nav-search"'
check_not_contains public/index.html 'href="book/toc.html"'
check_not_contains public/index.html 'West Africa Petroleum Reference'
check_contains public/index.html '<span class="hero-title-line">West Africa&#39;s</span><span class="hero-title-line">Independent Petroleum Reference</span>'
check_contains public/index.html 'Independent reference material covering petroleum systems, fiscal regimes, governance frameworks, national oil companies, upstream operations, and country-specific petroleum sectors across West Africa.'
check_contains public/index.html 'class="hero-stat-grid"'
check_contains public/index.html 'Start Reading</a>'
check_contains public/index.html 'Browse Countries</a>'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-start-reading'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-menu'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-close'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-research.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-industry-monitoring.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-intelligence.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-production.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-exploration.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-fiscal.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-regulation.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-research.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-policy.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-operators.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-start-reading.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-menu.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-close.png'
check_contains public/index.html 'class="button-icon ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm"'
check_not_contains public/index.html 'class="mobile-nav-contact"'
check_not_contains public/index.html '>Contact Us</a>'
check_contains public/index.html 'class="section section-platform decision-strip"'
check_contains public/index.html 'Built for informed decision-making'
check_contains public/index.html '<span class="decision-strip-title-line">Built for informed</span><span class="decision-strip-title-line">decision-making</span>'
check_contains public/index.html 'class="section-divider section-divider-country-discovery"'
check_contains public/index.html 'class="stakeholder-grid"'
check_contains public/index.html 'class="stakeholder-card stakeholder-card--governments"'
check_contains public/index.html 'class="stakeholder-icon-slot"'
check_contains public/index.html 'class="stakeholder-copy-slot"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/governments.png"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/regulators.png"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/national-oil-companies.png"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/operators.png"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/investors.png"'
check_contains public/index.html 'class="stakeholder-icon stakeholder-icon-image" src="/assets/icons/stakeholders/universities-researchers.png"'
check_not_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-policy'
check_not_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-national-oil-companies'
check_not_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-industry-monitoring'
check_not_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-investors'
check_not_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-research'
check_contains public/index.html '<span class="stakeholder-label-line">National Oil</span><span class="stakeholder-label-line">Companies</span>'
check_contains public/index.html '<span class="stakeholder-label-line">Universities &amp;</span><span class="stakeholder-label-line">Researchers</span>'
check_not_contains public/index.html 'class="stakeholder-chip"'
check_contains public/index.html 'class="country-grid-v2"'
check_contains public/index.html 'class="country-card-v2 status-producing"'
check_contains public/index.html 'class="country-card-v2 status-exploration"'
check_contains public/index.html 'class="country-card-v2 status-noCommercialProduction"'
check_contains public/index.html '<symbol id="nigeria"'
check_contains public/index.html '<symbol id="ghana"'
check_contains public/index.html 'class="country-flag-media country-flag-media-card"'
check_contains public/index.html '<use href="#nigeria"></use>'
check_contains public/index.html '<use href="#ghana"></use>'
check_not_contains public/index.html '/assets/icons/country-flags.svg#nigeria'
check_not_contains public/index.html '/assets/icons/country-flags.svg#ghana'
check_contains public/index.html 'assets/images/homepage-west-africa-map-panel.png'
check_contains public/index.html 'assets/images/homepage-west-africa-map-panel@2x.png 2x'
check_not_contains public/index.html 'assets/images/homepage-west-africa-map-panel.webp'
check_not_contains public/index.html '🇳🇬'
check_contains public/index.html 'View All Countries'
check_contains public/index.html 'Country Analysis <span aria-hidden="true">→</span></a>'
check_contains public/index.html 'class="section-heading section-heading-centered"'
check_contains public/index.html 'Search Upstream Atlas'
check_contains public/index.html 'class="search-scope-chip" href="/book/?search=Fiscal%20Systems"'
check_contains public/index.html 'class="topic-grid"'
check_contains public/index.html 'Governance &amp; Regulation'
check_contains public/index.html 'class="summary-card-eyebrow">Latest Updates</p>'
check_contains public/index.html 'class="summary-card-eyebrow">Current Edition</p>'
check_contains public/index.html 'class="summary-card-eyebrow">Topics Covered</p>'
check_contains public/index.html 'class="summary-card-eyebrow">Future Development</p>'
check_contains public/index.html 'class="site-footer site-footer-detailed"'
check_contains public/index.html 'class="brand-mark-image brand-mark-image-full"'
check_contains public/index.html 'class="brand-mark-image brand-mark-image-compact"'
check_contains public/index.html 'Terms of Use'
check_contains public/index.html 'Privacy Policy'
check_contains public/index.html 'Cookie Policy'
check_not_contains public/index.html 'class="footer-brand-lockup"'
check_not_contains public/index.html 'footer-brand-surface'
check_not_contains public/index.html 'upstream-atlas-wordmark.png'
check_not_contains public/index.html 'upstream-atlas-logo.png'
check_contains public/index.html 'fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap'
check_exists public/assets/icons/homepage/icon-research.svg
check_exists public/assets/icons/homepage/icon-industry-monitoring.svg
check_exists public/assets/icons/homepage/icon-intelligence.svg
check_exists public/assets/icons/homepage/icon-start-reading.svg
check_exists public/assets/icons/homepage/icon-menu.svg
check_exists public/assets/icons/homepage/icon-close.svg
check_exists public/assets/icons/homepage/icon-production.svg
check_exists public/assets/icons/homepage/icon-exploration.svg
check_exists public/assets/icons/homepage/icon-fiscal.svg
check_exists public/assets/icons/homepage/icon-regulation.svg
check_exists public/assets/icons/homepage-cropped/icon-research.webp
check_exists public/assets/icons/homepage-cropped/icon-industry-monitoring.webp
check_exists public/assets/icons/homepage-cropped/icon-intelligence.webp
check_exists public/assets/icons/homepage-cropped/icon-production.webp
check_exists public/assets/icons/homepage-cropped/icon-exploration.webp
check_exists public/assets/icons/homepage-cropped/icon-fiscal.webp
check_exists public/assets/icons/homepage-cropped/icon-regulation.webp
check_exists public/assets/icons/homepage-cropped/icon-audience-research.webp
check_exists public/assets/icons/homepage-cropped/icon-audience-policy.webp
check_exists public/assets/icons/homepage-cropped/icon-audience-operators.webp
check_exists public/assets/icons/homepage/icon-audience-research.svg
check_exists public/assets/icons/homepage/icon-audience-policy.svg
check_exists public/assets/icons/homepage/icon-audience-operators.svg
check_exists public/assets/icons/homepage-sprite.svg
check_exists public/assets/icons/stakeholders/governments.png
check_exists public/assets/icons/stakeholders/regulators.png
check_exists public/assets/icons/stakeholders/national-oil-companies.png
check_exists public/assets/icons/stakeholders/operators.png
check_exists public/assets/icons/stakeholders/investors.png
check_exists public/assets/icons/stakeholders/universities-researchers.png
python3 scripts/check_stakeholder_icon_geometry.py
check_exists public/assets/icons/country-flags.svg
check_exists public/assets/images/upstream-atlas-nav-logo.webp
check_exists public/assets/images/upstream-atlas-hero-v7-clean-left.webp
check_exists assets/images/homepage-west-africa-map-panel.png
check_exists assets/images/homepage-west-africa-map-panel@2x.png
check_exists public/assets/images/homepage-west-africa-map-panel.png
check_exists public/assets/images/homepage-west-africa-map-panel@2x.png
check_exists public/assets/images/prototype-hero-graywhite-left.webp
check_exists public/assets/images/prototype-hero-graywhite-right.webp
check_exists assets/css/landing.base.css
check_exists assets/css/landing.header.css
check_exists assets/css/landing.hero.css
check_exists assets/css/landing.sections.css
check_exists assets/css/landing.components.css
check_exists assets/css/landing.footer.css
check_exists assets/css/landing.homepage-v2.css
check_exists assets/css/landing.discovery.css
check_exists assets/css/landing.modules.css
check_exists assets/css/landing.responsive-tablet.css
check_exists assets/css/landing.responsive-mobile.css
check_line_count_at_most assets/css/landing.css 20
check_line_count_at_most assets/css/landing.base.css 500
check_line_count_at_most assets/css/landing.header.css 500
check_line_count_at_most assets/css/landing.hero.css 500
check_line_count_at_most assets/css/landing.sections.css 500
check_line_count_at_most assets/css/landing.components.css 500
check_line_count_at_most assets/css/landing.footer.css 500
check_line_count_at_most assets/css/landing.homepage-v2.css 500
check_line_count_at_most assets/css/landing.discovery.css 500
check_line_count_at_most assets/css/landing.modules.css 500
check_line_count_at_most assets/css/landing.responsive-tablet.css 500
check_line_count_at_most assets/css/landing.responsive-mobile.css 500
check_file_size_at_most public/assets/images/upstream-atlas-icon.png 50000
check_file_size_at_most public/assets/images/upstream-atlas-wordmark.png 110000
check_file_size_at_most public/assets/images/upstream-atlas-nav-logo.webp 80000
check_image_has_no_opaque_white_fringe public/assets/images/upstream-atlas-nav-logo.webp 50
check_file_size_at_most public/assets/images/prototype-hero.jpg 120000
check_file_size_at_most public/assets/images/prototype-hero-graywhite-left.webp 25000
check_file_size_at_most public/assets/images/prototype-hero-graywhite-right.webp 25000
LANDING_CSS_ASSERT_FILE="$(create_temp_file "landing-css-check." ".css")"
build_expanded_landing_css_check_file "$LANDING_CSS_ASSERT_FILE"
check_contains assets/css/landing.css '@import "./landing.base.css";'
check_contains assets/css/landing.css '@import "./landing.header.css";'
check_contains assets/css/landing.css '@import "./landing.hero.css";'
check_contains assets/css/landing.css '@import "./landing.sections.css";'
check_contains assets/css/landing.css '@import "./landing.components.css";'
check_contains assets/css/landing.css '@import "./landing.footer.css";'
check_contains assets/css/landing.css '@import "./landing.homepage-v2.css";'
check_contains assets/css/landing.css '@import "./landing.discovery.css";'
check_contains assets/css/landing.css '@import "./landing.modules.css";'
check_contains assets/css/landing.css '@import "./landing.responsive-tablet.css";'
check_contains assets/css/landing.css '@import "./landing.responsive-mobile.css";'
check_contains "$LANDING_CSS_ASSERT_FILE" '--page-bg: #f7f8f9;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--surface-muted: #eef2f4;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--ink-primary: #0b1f33;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--brand-blue: #3163c2;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--brand-blue-deep: #264d97;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--footer-bg: #0b1f33;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--secondary: #d88a1d;'
check_contains "$LANDING_CSS_ASSERT_FILE" '--text: var(--ink-primary);'
check_contains "$LANDING_CSS_ASSERT_FILE" 'background: url("../images/upstream-atlas-hero-v7-clean-left.webp") center center / cover no-repeat;'
check_contains "$LANDING_CSS_ASSERT_FILE" 'filter: saturate(1.08) contrast(1.1) brightness(1.08);'
check_contains "$LANDING_CSS_ASSERT_FILE" 'background: #0a213a;'
check_contains "$LANDING_CSS_ASSERT_FILE" 'circle at 85% 50%'
check_contains "$LANDING_CSS_ASSERT_FILE" 'rgba(10, 33, 58, 1) 50%'
check_contains "$LANDING_CSS_ASSERT_FILE" 'width: min(100%, 54rem);'
check_contains "$LANDING_CSS_ASSERT_FILE" '.section-country-discovery {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'padding-top: 0;'
check_contains "$LANDING_CSS_ASSERT_FILE" '.decision-strip {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'padding-block: 2.2rem 0;'
check_contains "$LANDING_CSS_ASSERT_FILE" '.section-divider-country-discovery {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'margin-block: 24px;'
check_contains "$LANDING_CSS_ASSERT_FILE" 'border-top: 1px solid var(--line);'
check_not_contains "$LANDING_CSS_ASSERT_FILE" '.section-country-discovery .section-heading-wide {'
check_not_contains "$LANDING_CSS_ASSERT_FILE" '--primary: #264d97;'
check_contains "$LANDING_CSS_ASSERT_FILE" '@media (min-width: 1024px) {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.hero-signal-panel {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'margin-top: clamp(17rem, 30vw, 20.5rem);'
check_contains "$LANDING_CSS_ASSERT_FILE" '.chapters-link-row {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'width: min(90rem, calc(100% - 4rem));'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".decision-strip-inner {");if(start===-1){console.error("Expected .decision-strip-inner rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .decision-strip-inner rule block.");process.exit(1);}const block=css.slice(start, end + 1);if(!block.includes("width: min(90rem, calc(100% - 4rem));")){console.error("Expected .decision-strip-inner to match the shared 90rem content width aligned with the hero call-to-action baseline.");process.exit(1);}if(!block.includes("grid-template-columns: minmax(0, 1.105fr) minmax(0, 1.195fr);")){console.error("Expected .decision-strip-inner to use the 3-line-title compromise proportions.");process.exit(1);}for(const removed of ["width: min(76rem, calc(100% - 2rem));","width: min(84rem, calc(100% - 2rem));","grid-template-columns: minmax(0, 1.06fr) minmax(0, 1.24fr);","grid-template-columns: minmax(0, 1.18fr) minmax(0, 1.12fr);"]){if(block.includes(removed)){console.error(`Expected .decision-strip-inner to stop using ${removed}.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".decision-strip-copy {");if(start===-1){console.error("Expected .decision-strip-copy rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .decision-strip-copy rule block.");process.exit(1);}const block=css.slice(start, end + 1);for(const expected of ["grid-template-columns: max-content minmax(15rem, 1fr);","column-gap: 2rem;","row-gap: 0;"]){if(!block.includes(expected)){console.error(`Expected .decision-strip-copy to include ${expected} so the supporting copy starts from the true rendered title-column width with doubled spacing.`);process.exit(1);}}for(const removed of ["column-gap: 1rem;","column-gap: 0.5rem;","grid-template-columns: minmax(17.15rem, 17.85rem) minmax(15rem, 1fr);","grid-template-columns: minmax(17.9rem, 18.6rem) minmax(15rem, 1fr);","grid-template-columns: minmax(15.85rem, 17.1rem) minmax(14.7rem, 1fr);","grid-template-columns: minmax(15.25rem, 16.5rem) minmax(15rem, 1fr);","gap: 0.72rem;","gap: 0.8rem;","grid-template-columns: minmax(17rem, 18.5rem) minmax(16.5rem, 1fr);","gap: 0.95rem;","gap: 0.86rem;"]){if(block.includes(removed)){console.error(`Expected .decision-strip-copy to stop using ${removed}.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".decision-strip-copy h2 {");if(start===-1){console.error("Expected .decision-strip-copy h2 rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .decision-strip-copy h2 rule block.");process.exit(1);}const block=css.slice(start, end + 1);for(const expected of ["width: max-content;","max-width: none;","font-size: clamp(1.58rem, 1.64vw, 1.9rem);","line-height: 1.08;","letter-spacing: 0;"]){if(!block.includes(expected)){console.error(`Expected .decision-strip-copy h2 to include ${expected} so the title column matches its actual content width.`);process.exit(1);}}for(const removed of ["max-width: 18rem;","max-width: 16.6rem;","font-size: clamp(1.64rem, 1.76vw, 2rem);","letter-spacing: -0.04em;","text-wrap: balance;"]){if(block.includes(removed)){console.error(`Expected .decision-strip-copy h2 to stop using ${removed}.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".decision-strip-title-line {");if(start===-1){console.error("Expected .decision-strip-title-line rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .decision-strip-title-line rule block.");process.exit(1);}const block=css.slice(start, end + 1);for(const expected of ["display: block;","white-space: nowrap;"]){if(!block.includes(expected)){console.error(`Expected .decision-strip-title-line to include ${expected} for a fixed two-line title layout.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".decision-strip-copy p {");if(start===-1){console.error("Expected .decision-strip-copy p rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .decision-strip-copy p rule block.");process.exit(1);}const block=css.slice(start, end + 1);for(const expected of ["max-width: 21rem;","padding-top: 0;","font-size: 0.875rem;","line-height: 1.54;"]){if(!block.includes(expected)){console.error(`Expected .decision-strip-copy p to include ${expected} so the supporting copy sits closer to the design density.`);process.exit(1);}}for(const removed of ["padding-top: 0.25rem;","font-size: 0.94rem;","font-size: 0.9rem;","line-height: 1.68;","line-height: 1.6;"]){if(block.includes(removed)){console.error(`Expected .decision-strip-copy p to stop using ${removed}.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const start=css.indexOf(".stakeholder-grid {");if(start===-1){console.error("Expected .stakeholder-grid rule block in expanded landing CSS.");process.exit(1);}const end=css.indexOf("}", start);if(end===-1){console.error("Expected closing brace for .stakeholder-grid rule block.");process.exit(1);}const block=css.slice(start, end + 1);for(const expected of ["grid-template-columns: repeat(6, 120px);","justify-content: end;","justify-items: center;","align-items: start;","gap: 12px;"]){if(!block.includes(expected)){console.error(`Expected .stakeholder-grid to include ${expected} so fixed-width cards keep a true 12px visual gap.`);process.exit(1);}}for(const removed of ["grid-template-columns: repeat(6, minmax(0, 1fr));","grid-template-columns: repeat(6, minmax(7.4rem, 1fr));","gap: 8px;","gap: 0.96rem;","gap: 0.885rem;","gap: 0.84rem;","gap: 0.82rem;"]){if(block.includes(removed)){console.error(`Expected .stakeholder-grid to stop using ${removed}.`);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e '
const fs = require("fs");
const css = fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE, "utf8");

function getBlock(selector) {
  const start = css.indexOf(selector + " {");
  if (start === -1) {
    console.error(`Expected ${selector} rule block in expanded landing CSS.`);
    process.exit(1);
  }
  const end = css.indexOf("}", start);
  if (end === -1) {
    console.error(`Expected closing brace for ${selector} rule block.`);
    process.exit(1);
  }
  return css.slice(start, end + 1);
}

const stakeholderCard = getBlock(".stakeholder-card");
for (const expected of [
  "--stakeholder-icon-color: #2d5cb3;",
  "--stakeholder-icon-size: 78px;",
  "--stakeholder-icon-offset-x: 0px;",
  "--stakeholder-icon-offset-y: 0px;",
  "--stakeholder-icon-scale: 1;",
  "--stakeholder-text-color: #214484;",
  "align-self: start;",
  "box-sizing: border-box;",
  "grid-template-rows: 82px 37px;",
  "align-content: center;",
  "width: 120px;",
  "min-width: 120px;",
  "max-width: 120px;",
  "height: 154px;",
  "min-height: 154px;",
  "max-height: 154px;",
  "row-gap: 9px;",
  "padding: 15px 9px 11px;",
  "border-radius: 0.96rem;",
  "box-shadow: 0 8px 20px rgba(11, 31, 51, 0.045);",
  "color: var(--stakeholder-text-color);",
]) {
  if (!stakeholderCard.includes(expected)) {
    console.error(
      `Expected .stakeholder-card to include ${expected} so the stakeholder icons stay optically aligned within fixed cards.`,
    );
    process.exit(1);
  }
}

for (const removed of [
  "aspect-ratio: 1 / 1;",
  "gap: 0.48rem;",
  "gap: 0.84rem;",
  "gap: 0.78rem;",
  "gap: 0.72rem;",
  "gap: 0.82rem;",
  "max-width: 100%;",
  "min-height: auto;",
  "min-height: 9.55rem;",
  "min-height: 9.35rem;",
  "min-height: 9.45rem;",
  "padding: 0.25rem 0.56rem 0.5rem;",
  "padding: 1.02rem 0.62rem 0.98rem;",
  "padding: 1.14rem 0.64rem 0.96rem;",
  "padding: 1.18rem 0.7rem 0.9rem;",
  "padding: 1.28rem 0.75rem 0.95rem;",
  "border-radius: 0.92rem;",
  "border-radius: 1rem;",
  "box-shadow: 0 6px 18px rgba(11, 31, 51, 0.045);",
  "color: var(--brand-blue-deep);",
]) {
  if (stakeholderCard.includes(removed)) {
    console.error(`Expected .stakeholder-card to stop using ${removed}.`);
    process.exit(1);
  }
}

const iconSlot = getBlock(".stakeholder-icon-slot");
for (const expected of [
  "display: grid;",
  "place-items: center;",
  "align-self: stretch;",
  "justify-self: stretch;",
  "min-height: 82px;",
]) {
  if (!iconSlot.includes(expected)) {
    console.error(`Expected .stakeholder-icon-slot to include ${expected} so icons share one fixed container.`);
    process.exit(1);
  }
}

const stakeholderIcon = getBlock(".stakeholder-icon");
for (const expected of [
  "display: block;",
  "align-self: center;",
  "justify-self: center;",
  "width: var(--stakeholder-icon-size);",
  "height: var(--stakeholder-icon-size);",
  "margin-top: 0;",
  "color: var(--stakeholder-icon-color);",
  "transform: translate(var(--stakeholder-icon-offset-x), var(--stakeholder-icon-offset-y))",
  "scale(var(--stakeholder-icon-scale));",
  "transform-origin: center center;",
]) {
  if (!stakeholderIcon.includes(expected)) {
    console.error(`Expected .stakeholder-icon to include ${expected} for per-icon centering.`);
    process.exit(1);
  }
}

for (const removed of [
  "width: 4rem;",
  "height: 4rem;",
  "width: 2rem;",
  "height: 2rem;",
  "margin-top: -0.04rem;",
  "margin-top: -0.08rem;",
  "transform: translateY(var(--stakeholder-icon-offset-y));",
]) {
  if (stakeholderIcon.includes(removed)) {
    console.error(`Expected .stakeholder-icon to stop using ${removed}.`);
    process.exit(1);
  }
}

const stakeholderImage = getBlock(".stakeholder-icon-image");
for (const expected of [
  "display: block;",
  "object-fit: contain;",
  "object-position: center center;",
]) {
  if (!stakeholderImage.includes(expected)) {
    console.error(
      `Expected .stakeholder-icon-image to include ${expected} so standalone PNG assets align like sprite icons.`,
    );
    process.exit(1);
  }
}

const copySlot = getBlock(".stakeholder-copy-slot");
for (const expected of [
  "display: grid;",
  "align-self: stretch;",
  "justify-self: stretch;",
  "align-content: start;",
  "min-height: 2.32rem;",
]) {
  if (!copySlot.includes(expected)) {
    console.error(`Expected .stakeholder-copy-slot to include ${expected} so labels share one fixed container.`);
    process.exit(1);
  }
}

const stakeholderLabel = getBlock(".stakeholder-label");
for (const expected of [
  "gap: 0.02rem;",
  "align-content: start;",
  "min-height: 100%;",
  "color: var(--stakeholder-text-color);",
  "font-size: 0.72rem;",
  "font-weight: 600;",
  "line-height: 1.08;",
]) {
  if (!stakeholderLabel.includes(expected)) {
    console.error(`Expected .stakeholder-label to include ${expected} so multi-line labels top-align within the copy slot.`);
    process.exit(1);
  }
}

for (const removed of [
  "gap: 0.06rem;",
  "gap: 0.04rem;",
  "min-height: auto;",
  "min-height: 2.34rem;",
  "min-height: 2.42rem;",
  "min-height: 2.26rem;",
  "font-size: 0.79rem;",
  "font-size: 0.76rem;",
  "line-height: 1.18;",
  "line-height: 1.2;",
  "line-height: 1.22;",
]) {
  if (stakeholderLabel.includes(removed)) {
    console.error(`Expected .stakeholder-label to stop using ${removed}.`);
    process.exit(1);
  }
}

const governmentsCard = getBlock(".stakeholder-card--governments");
for (const expected of ["--stakeholder-icon-size: 80px;"]) {
  if (!governmentsCard.includes(expected)) {
    console.error(`Expected .stakeholder-card--governments to include ${expected} for optical centering.`);
    process.exit(1);
  }
}

const regulatorsCard = getBlock(".stakeholder-card--regulators");
for (const expected of ["--stakeholder-icon-size: 74px;"]) {
  if (!regulatorsCard.includes(expected)) {
    console.error(`Expected .stakeholder-card--regulators to include ${expected} for optical centering.`);
    process.exit(1);
  }
}

const nocCard = getBlock(".stakeholder-card--national-oil-companies");
for (const expected of ["--stakeholder-icon-size: 76px;"]) {
  if (!nocCard.includes(expected)) {
    console.error(
      `Expected .stakeholder-card--national-oil-companies to include ${expected} for optical centering.`,
    );
    process.exit(1);
  }
}

const operatorsCard = getBlock(".stakeholder-card--operators");
for (const expected of ["--stakeholder-icon-size: 80px;"]) {
  if (!operatorsCard.includes(expected)) {
    console.error(`Expected .stakeholder-card--operators to include ${expected} for optical centering.`);
    process.exit(1);
  }
}

const investorsCard = getBlock(".stakeholder-card--investors");
for (const expected of ["--stakeholder-icon-size: 78px;"]) {
  if (!investorsCard.includes(expected)) {
    console.error(`Expected .stakeholder-card--investors to include ${expected} for optical centering.`);
    process.exit(1);
  }
}

const universitiesCard = getBlock(".stakeholder-card--universities-researchers");
for (const expected of ["--stakeholder-icon-size: 78px;"]) {
  if (!universitiesCard.includes(expected)) {
    console.error(
      `Expected .stakeholder-card--universities-researchers to include ${expected} for optical centering.`,
    );
    process.exit(1);
  }
}
'
check_contains "$LANDING_CSS_ASSERT_FILE" '.chapters-link {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'margin: 0;'
check_contains "$LANDING_CSS_ASSERT_FILE" 'border-radius: 0.5rem;'
check_contains "$LANDING_CSS_ASSERT_FILE" 'font-weight: 500;'
check_contains "$LANDING_CSS_ASSERT_FILE" '.brand-mark-image {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.brand-mark-image-compact {'
check_not_contains "$LANDING_CSS_ASSERT_FILE" '.footer-brand-surface {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'font-family: "Manrope", "Inter", sans-serif;'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-toggle {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-toggle .mobile-nav-icon-close {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.header-actions {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.header-contact-link::after {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-contact {'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const compactLogoRule=/@media \(max-width: 767px\) \{[\s\S]*?\.brand-mark-image-full \{[^}]*display: none;[^}]*\}[\s\S]*?\.brand-mark-image-compact \{[^}]*display: block;[^}]*\}/;if(!compactLogoRule.test(css)){console.error("Expected landing header to switch to the compact logo below 768px.");process.exit(1);}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const match=css.match(/@media \(max-width: 767px\) \{[\s\S]*?\.site-header \.brand-mark \{[\s\S]*?\.site-header[\s\S]*?\.mobile-nav-toggle[\s\S]*?\.ua-icon--sm \{[\s\S]*?\}/);if(!match){console.error("Expected phone landing header media block with compact-brand and nav-toggle rules.");process.exit(1);}const block=match[0];for(const expected of [".site-header .brand-mark {","min-width: 2.75rem;","min-height: 2.75rem;","justify-content: center;",".site-header .brand-mark-image-compact {","width: 2rem;"]){if(!block.includes(expected)){console.error("Expected narrow landing header logo CSS to include "+expected);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const match=css.match(/@media \(max-width: 767px\) \{[\s\S]*?\.site-header \.brand-mark \{[\s\S]*?\.site-header[\s\S]*?\.mobile-nav-toggle[\s\S]*?\.ua-icon--sm \{[\s\S]*?\}/);if(!match){console.error("Expected phone landing header media block with compact-brand and nav-toggle rules.");process.exit(1);}const block=match[0];for(const expected of [".site-header .header-actions > .site-language-switch {","min-height: 2.75rem;","gap: 0;","padding: 0 0.125rem;","background: transparent;","border-color: transparent;","isolation: isolate;",".site-header .header-actions > .site-language-switch::before {","inset: 0.1875rem 0;","content: \"\";",".site-header .header-actions > .site-language-switch .site-language-option {","min-width: 2.75rem;","min-height: 2.75rem;","padding: 0 0.4rem;","font-size: 0.78rem;",".site-language-option.is-current::before,","a.site-language-option:hover::before,","inset: 0.25rem 0.16rem;",".site-header .header-actions > .mobile-nav-menu .mobile-nav-toggle {","gap: 0.35rem;","padding: 0 0.75rem;","font-size: 0.82rem;",".site-header .header-actions > .mobile-nav-menu .mobile-nav-toggle::before {"]){if(!block.includes(expected)){console.error("Expected narrow landing header CSS to include "+expected);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const match=css.match(/@media \(min-width: 768px\) and \(max-width: 1023px\) \{[\s\S]*?\.site-header \.brand-mark \{[\s\S]*?\.site-header \.brand-mark-image-compact \{[\s\S]*?display: none;[\s\S]*?\}/);if(!match){console.error("Expected landing tablet header logo media block in expanded landing CSS.");process.exit(1);}const block=match[0];for(const expected of [".site-header .brand-mark {","width: auto;","height: 44px;","flex: 0 0 auto;",".site-header .brand-mark-image-full {","width: auto;","height: 36px;",".site-header .brand-mark-image-compact {","display: none;"]){if(!block.includes(expected)){console.error("Expected landing tablet header logo CSS to include "+expected);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const match=css.match(/@media \(min-width: 1024px\) and \(max-width: 1439px\) \{[\s\S]*?\.site-header \.brand-mark-image-full \{[\s\S]*?height: 36px;[\s\S]*?\}/);if(!match){console.error("Expected landing small-desktop header media block in expanded landing CSS.");process.exit(1);}const block=match[0];for(const expected of [".site-header .brand-mark-image-full {","width: auto;","height: 36px;"]){if(!block.includes(expected)){console.error("Expected landing small-desktop header CSS to include "+expected);process.exit(1);}}'
LANDING_CSS_ASSERT_FILE="$LANDING_CSS_ASSERT_FILE" node -e 'const fs=require("fs");const css=fs.readFileSync(process.env.LANDING_CSS_ASSERT_FILE,"utf8");const compactStart=css.indexOf("@media (max-width: 360px) {");if(compactStart===-1){console.error("Expected extra-narrow landing header media block in expanded landing CSS.");process.exit(1);}const compactBlock=css.slice(compactStart);for(const removed of ["min-width: 1.85rem;","width: 2.5rem;"]){if(compactBlock.includes(removed)){console.error("Expected extra-narrow landing header to keep the compact logo touch target while avoiding oversized visual overrides: "+removed);process.exit(1);}}'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon-image {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon--feature {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon-image--feature {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon-image--signal {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.feature-card-icon {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.button-icon {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-icon-close {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-menu[open] .mobile-nav-toggle .mobile-nav-icon-close {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.country-signal-icon {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.country-signal-copy {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.ua-icon--audience {'
check_contains "$LANDING_CSS_ASSERT_FILE" '@media (max-width: 767px) {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.site-header-inner {'
check_contains "$LANDING_CSS_ASSERT_FILE" 'grid-template-columns: auto auto;'
check_contains "$LANDING_CSS_ASSERT_FILE" '@media (max-width: 360px) {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.brand-mark-image-full {'
check_contains "$LANDING_CSS_ASSERT_FILE" '.mobile-nav-toggle .button-label {'
check_not_contains assets/css/landing.css '@import url("https://fonts.googleapis.com'
check_not_contains scripts/generate-chapters-page.mjs 'replaceAll('
check_not_contains assets/css/chapters.css 'var(--primary)'
check_not_contains assets/css/chapters.css '--primary:'
check_contains assets/css/chapters.css 'var(--ink-primary)'
check_contains assets/css/chapters.css 'var(--brand-blue)'

check_exists public/chapters/index.html
check_contains public/chapters/index.html 'Chapter Library'
check_contains public/chapters/index.html 'class="site-header-inner"'
check_contains public/chapters/index.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/chapters/index.html 'upstream-atlas-nav-logo.png'
check_contains public/chapters/index.html 'upstream-atlas-icon.png'
check_contains public/chapters/index.html 'class="button button-header" href="/book/">'
check_contains public/chapters/index.html '<span class="button-label">Start Reading</span>'
check_contains public/chapters/index.html '../assets/icons/homepage-sprite.svg#icon-start-reading'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-start-reading.png'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-menu.png'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-close.png'
check_contains public/chapters/index.html 'class="current-link" href="/chapters/">Chapters</a>'
check_contains public/chapters/index.html 'href="/#countries">Countries</a>'
check_contains public/chapters/index.html 'href="/#search">Search</a>'
check_not_contains public/chapters/index.html 'href="/#about">About</a>'
check_not_contains public/chapters/index.html 'href="/#resources">Resources</a>'
check_contains public/chapters/index.html 'mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas%20Enquiry'
check_not_contains public/chapters/index.html 'class="mobile-nav-contact"'
check_not_contains public/chapters/index.html '>Contact Us</a>'
node -e 'const fs=require("fs");for(const file of ["public/index.html","public/chapters/index.html","public/fr/index.html","public/fr/chapters/index.html"]){const html=fs.readFileSync(file,"utf8");if(/<nav class="mobile-nav-panel"[\s\S]*?class="site-language-switch"/.test(html)){console.error(`Expected ${file} to remove the language switch from the mobile navigation panel.`);process.exit(1);}}'
check_not_contains public/index.html '<path d="M5 4.75A1.75 1.75 0 0 1 6.75 3h8.5A1.75 1.75 0 0 1 17 4.75v14.5A1.75 1.75 0 0 1 15.25 21h-8.5A1.75 1.75 0 0 1 5 19.25Z'
check_contains public/chapters/index.html 'class="site-footer site-footer-detailed"'
check_contains public/chapters/index.html 'Terms of Use'
check_contains public/chapters/index.html 'Privacy Policy'
check_contains public/chapters/index.html 'Cookie Policy'
check_contains public/chapters/index.html 'fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap'
check_not_contains public/chapters/index.html 'class="nav-search"'
check_not_contains public/chapters/index.html 'href="../#audience"'
check_not_contains public/chapters/index.html 'class="footer-brand-lockup"'
check_not_contains public/chapters/index.html 'footer-brand-surface'
check_not_contains public/chapters/index.html 'upstream-atlas-wordmark.png'
check_not_contains public/chapters/index.html 'upstream-atlas-logo.png'
check_contains public/chapters/index.html '<h2>Part I: Regional Foundations</h2>'
check_contains public/chapters/index.html 'class="chapter-card-header"'
check_contains public/chapters/index.html 'class="chapter-card-status"'
check_contains public/chapters/index.html 'class="chapter-card-reading"'
check_contains public/chapters/index.html 'data-tooltip="Estimated reading time based on'
check_contains public/chapters/index.html 'Estimated reading time based on'
check_contains public/chapters/index.html 'Estimated reading time based on about 64 words and a front-matter overview pace.'
check_contains public/chapters/index.html 'Additional Resources'
check_not_contains public/chapters/index.html 'Open chapter'
check_not_contains public/chapters/index.html ' entries</p>'
check_not_contains public/chapters/index.html 'title="Estimated reading time based on'
check_contains public/chapters/index.html 'General Introduction'
check_contains public/chapters/index.html '/book/chapters/chapter-01-general-introduction.html'

check_exists public/terms-of-use.html
check_exists public/privacy-policy.html
check_exists public/cookie-policy.html
check_contains public/terms-of-use.html 'class="legal-page"'
check_contains public/privacy-policy.html 'class="legal-page"'
check_contains public/cookie-policy.html 'class="legal-page"'
check_contains public/terms-of-use.html 'Document pending final approved text'
check_contains public/privacy-policy.html 'Document pending final approved text'
check_contains public/cookie-policy.html 'Document pending final approved text'
check_contains public/terms-of-use.html 'Status: Final approved text pending publication'
check_contains public/privacy-policy.html 'Status: Final approved text pending publication'
check_contains public/cookie-policy.html 'Status: Final approved text pending publication'
check_contains public/terms-of-use.html 'href="privacy-policy.html"'
check_contains public/privacy-policy.html 'href="cookie-policy.html"'
check_contains public/cookie-policy.html 'href="terms-of-use.html"'
check_contains public/terms-of-use.html 'href="/"'
check_contains public/terms-of-use.html 'upstream-atlas-nav-logo.webp'
check_contains public/privacy-policy.html 'upstream-atlas-nav-logo.webp'
check_contains public/cookie-policy.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/terms-of-use.html 'upstream-atlas-nav-logo.png'
check_not_contains public/privacy-policy.html 'upstream-atlas-nav-logo.png'
check_not_contains public/cookie-policy.html 'upstream-atlas-nav-logo.png'
check_not_contains public/terms-of-use.html 'legal-page-brand-copy'
check_not_contains public/privacy-policy.html 'legal-page-brand-copy'
check_not_contains public/cookie-policy.html 'legal-page-brand-copy'
check_contains public/terms-of-use.html 'href="/"'
check_order public/terms-of-use.html '<p class="site-footer-heading">Coverage</p>' '<p class="site-footer-heading">Legal</p>'

check_contains public/book/index.html 'id="mdbook-sidebar"'
check_contains public/book/index.html 'class="light sidebar-visible"'
check_contains public/book/index.html 'id="book-progress-fill"'
check_contains public/book/index.html 'class="book-toolbar"'
check_contains public/book/index.html 'class="toolbar-sidebar"'
check_contains public/book/index.html 'class="toolbar-main"'
check_contains public/book/index.html 'class="toolbar-actions"'
check_not_contains public/book/index.html 'class="toolbar-left"'
check_not_contains public/book/index.html 'class="toolbar-right"'
check_contains public/book/index.html 'class="toolbar-line-icon toolbar-line-icon-menu"'
check_not_contains public/book/index.html 'M0 96C0 78.3 14.3 64 32 64H416'
check_contains public/book/index.html 'class="icon-button toolbar-link toolbar-contact-link"'
check_contains public/book/index.html 'class="toolbar-line-icon toolbar-line-icon-mail"'
check_contains public/book/index.html 'class="toolbar-line-icon toolbar-line-icon-search"'
check_not_contains public/book/index.html 'M416 208c0 45.9-14.9 88.3-40 122.7'
check_contains public/book/index.html 'href="mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas"'
check_contains public/book/index.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/book/index.html 'upstream-atlas-nav-logo.png'
check_contains public/book/index.html 'upstream-atlas-icon.png'
check_contains public/book/index.html 'class="book-home-icon book-home-icon-full"'
check_contains public/book/index.html 'class="book-home-icon book-home-icon-compact"'
check_contains public/book/index.html 'class="book-sidebar-intro"'
check_not_contains public/book/index.html 'Reader Edition'
check_contains public/book/index.html 'class="reader-sidebar-scroll"'
check_not_contains public/book/index.html 'class="book-sidebar-utilities"'
check_not_contains public/book/index.html 'Reference Surfaces'
check_not_contains public/book/index.html 'class="book-sidebar-download"'
check_not_contains public/book/index.html 'href="../assets/book/upstream-atlas-reader.pdf"'
check_contains public/book/index.html 'class="toolbar-link-label"'
check_contains public/book/index.html 'class="reader-chapter-hero-anchor"'
check_contains public/book/index.html 'class="book-outline-section book-outline-figures"'
check_contains public/book/index.html 'class="book-outline-section book-outline-tables"'
check_contains public/book/index.html 'title="Contact Us"'
check_not_contains public/book/index.html 'title="Git repository"'
check_contains public/book/index.html 'class="reader-language-switch"'
check_contains public/book/index.html 'href="/fr/book/?lang=fr"'
check_order public/book/index.html 'data-reader-language-switch="toolbar"' 'class="icon-button toolbar-link toolbar-contact-link"'
check_order public/book/index.html 'class="icon-button toolbar-link toolbar-contact-link"' 'id="mdbook-search-toggle"'
check_contains public/book/index.html 'navigator.languages'
check_contains public/book/index.html 'rel="canonical" href="https://upstreamatlas.com/book/"'
check_contains public/book/index.html 'rel="alternate" hreflang="fr" href="https://upstreamatlas.com/fr/book/"'
check_contains public/book/index.html 'rel="alternate" hreflang="x-default" href="https://upstreamatlas.com/book/"'
check_contains public/book/index.html '"@type": "Book"'
check_contains public/book/index.html '"inLanguage": "en"'
check_contains public/book/index.html 'class="toolbar-search-slot hidden"'
check_contains public/book/index.html 'id="mdbook-search-wrapper" class="hidden"'
check_contains public/book/index.html 'id="mdbook-search-clear"'
check_contains public/book/index.html 'id="mdbook-content" class="content reader-layout"'
check_contains public/book/index.html 'reader-layout'
check_contains public/book/index.html 'reader-main'
check_contains public/book/index.html 'reader-outline'
check_contains public/book/index.html 'id="mdbook-reader-scroll"'
check_contains public/book/index.html 'id="mdbook-outline-scroll"'
check_contains public/book/index.html 'class="reader-main-inner"'
check_contains public/book/index.html 'reader-article'
check_contains public/book/index.html 'book-sidebar-shell'
check_not_contains public/book/index.html 'sidebar-resize-indicator'
check_not_contains public/book/index.html 'class="sidebar-resize-handle"'
check_not_contains public/book/index.html 'title="Print this book"'
check_not_contains public/book/index.html 'title="Suggest an edit"'
check_not_contains public/book/index.html 'title="Change theme"'
check_contains public/book/index.html 'class="book-outline-inner"'
check_contains public/book/index.html 'class="chapter-nav-card chapter-nav-next"'
check_exists public/book/reader-page-meta.json
check_contains public/book/reader-page-meta.json 'chapters/chapter-01-general-introduction.html'
node scripts/check_reader_runtime_build_contract.mjs
node scripts/check_reader_runtime_outline.mjs
run_browser_runtime_check_if_available
check_order public/book/index.html 'css/general-' 'theme/custom-'
check_not_contains public/book/toc.html 'href="index.html" target="_parent">Home</a>'
check_not_contains public/book/print.html 'title="Git repository"'
check_not_contains public/book/404.html 'title="Git repository"'
check_tree_not_contains public/book 'https://github.com/peakwalk/west-africa-petroleum-book'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'reader-layout'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'reader-main'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'reader-outline'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'reader-article'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'class="book-sidebar-download"'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'href="../../assets/book/upstream-atlas-reader.pdf"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'rel="canonical" href="https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'rel="alternate" hreflang="fr" href="https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'rel="alternate" hreflang="x-default" href="https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '"@type": "Chapter"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '"@type": "BreadcrumbList"'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '<meta name="description" content="">'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-024.webp'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-024.png'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-030.webp'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-030.png'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-031.webp'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-031.png'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-032.webp'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-032.png'
check_not_contains public/book/chapters/bibliographical-references.html 'TABLE OF CONTENTS'
check_contains public/book/chapters/disclaimer.html 'href="/fr/book/?lang=fr"'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html?lang=fr'
check_contains public/book/chapters/disclaimer.html 'rel="canonical" href="https://upstreamatlas.com/book/chapters/disclaimer.html"'
check_contains public/book/chapters/disclaimer.html 'rel="alternate" hreflang="x-default" href="https://upstreamatlas.com/book/chapters/disclaimer.html"'
check_not_contains public/book/chapters/disclaimer.html 'rel="alternate" hreflang="fr"'
check_contains public/book/chapters/cover.html 'rel="canonical" href="https://upstreamatlas.com/book/"'
check_contains public/book/chapters/cover.html 'meta name="robots" content="noindex,follow"'
check_contains public/book/chapters/cover.html 'http-equiv="refresh" content="0; url=../"'
check_contains public/book/chapters/front-matter.html 'rel="canonical" href="https://upstreamatlas.com/book/"'
check_contains public/book/chapters/front-matter.html 'meta name="robots" content="noindex,follow"'
check_contains public/book/chapters/front-matter.html 'http-equiv="refresh" content="0; url=../"'

check_exists public/book-sitemap.xml
check_exists public/robots.txt
check_contains public/book-sitemap.xml 'https://upstreamatlas.com/book/'
check_contains public/book-sitemap.xml 'https://upstreamatlas.com/fr/book/'
check_contains public/book-sitemap.xml 'https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html'
check_not_contains public/book-sitemap.xml 'https://upstreamatlas.com/book/chapters/cover.html'
check_not_contains public/book-sitemap.xml 'https://upstreamatlas.com/book/chapters/front-matter.html'
check_not_contains public/book-sitemap.xml 'https://upstreamatlas.com/fr/book/chapters/cover.html'
check_not_contains public/book-sitemap.xml 'https://upstreamatlas.com/fr/book/chapters/front-matter.html'
check_contains public/robots.txt 'User-agent: *'
check_contains public/robots.txt 'Allow: /'
check_contains public/robots.txt 'Sitemap: https://upstreamatlas.com/book-sitemap.xml'

check_exists public/fr/index.html
check_exists public/fr/chapters/index.html
check_exists public/fr/terms-of-use.html
check_exists public/fr/privacy-policy.html
check_exists public/fr/cookie-policy.html
check_exists public/fr/book/index.html
check_exists public/fr/book/reader-page-meta.json
check_exists public/fr/assets/images/upstream-atlas-nav-logo.webp
check_contains public/fr/index.html 'assets/css/landing.css?v=20260703'
check_contains public/fr/index.html 'class="site-language-switch"'
check_contains public/fr/index.html 'href="/?lang=en"'
check_contains public/fr/index.html '<span class="button-label">Commencer la lecture</span>'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-research.webp'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-industry-monitoring.webp'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-intelligence.webp'
check_contains public/fr/index.html 'assets/icons/homepage-sprite.svg#icon-start-reading'
check_contains public/fr/index.html 'assets/icons/homepage-sprite.svg#icon-menu'
check_contains public/fr/index.html 'assets/icons/homepage-sprite.svg#icon-close'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-research.webp'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-policy.webp'
check_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-operators.webp'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-research.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-industry-monitoring.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-intelligence.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-production.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-exploration.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-fiscal.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-regulation.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-research.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-policy.png'
check_not_contains public/fr/index.html 'assets/icons/homepage-cropped/icon-audience-operators.png'
check_contains public/fr/chapters/index.html 'Bibliothèque des chapitres'
check_contains public/fr/chapters/index.html 'href="/fr/book/"'
check_contains public/fr/terms-of-use.html 'Conditions d’utilisation'
check_contains public/fr/privacy-policy.html 'Politique de confidentialité'
check_contains public/fr/cookie-policy.html 'Politique relative aux cookies'
check_contains public/fr/book/chapters/glossary.html 'rel="canonical" href="https://upstreamatlas.com/fr/book/chapters/glossary.html"'
check_contains public/fr/book/chapters/glossary.html '"@type": "WebPage"'
check_contains public/fr/book/chapters/glossary.html '"@type": "BreadcrumbList"'
check_contains public/fr/book/chapters/general-introduction.html '"@type": "Chapter"'
check_contains public/fr/book/index.html 'class="reader-language-switch"'
check_contains public/fr/book/index.html 'aria-label="Changer de langue"'
check_contains public/fr/book/index.html 'href="/book/?lang=en"'
check_contains public/fr/book/index.html '"inLanguage": "fr"'
check_contains public/fr/book/chapters/foreword.html 'href="/book/chapters/foreword-to-the-french-edition.html?lang=en"'
check_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '/book/chapters/chapter-05-hydrocarbon-value-chain.html?lang=en'
check_contains public/fr/book/chapters/cover.html 'rel="canonical" href="https://upstreamatlas.com/fr/book/"'
check_contains public/fr/book/chapters/cover.html 'meta name="robots" content="noindex,follow"'
check_contains public/fr/book/chapters/cover.html 'http-equiv="refresh" content="0; url=../"'
check_contains public/fr/book/chapters/front-matter.html 'rel="canonical" href="https://upstreamatlas.com/fr/book/"'
check_contains public/fr/book/chapters/front-matter.html 'meta name="robots" content="noindex,follow"'
check_contains public/fr/book/chapters/front-matter.html 'http-equiv="refresh" content="0; url=../"'
check_contains public/fr/book/chapters/list-of-equations.html 'Liste des équations'
check_contains public/fr/book/chapters/list-of-tables.html 'aria-label="Navigation des chapitres"'
check_contains public/fr/book/chapters/list-of-tables.html '<span class="chapter-nav-label">Chapitre précédent</span>'
check_contains public/fr/book/chapters/list-of-tables.html '<span class="chapter-nav-label">Chapitre suivant</span>'
check_contains editions/en/content/SUMMARY.md 'chapters/chapter-01-general-introduction.md'
check_contains editions/en/content/SUMMARY.md 'chapters/chapter-05-hydrocarbon-value-chain.md'
check_contains editions/en/content/SUMMARY.md 'chapters/chapter-06-upstream-operations-and-government-roles.md'
check_contains editions/en/content/SUMMARY.md 'chapters/chapter-08-west-african-fiscal-regimes.md'
check_contains editions/en/content/SUMMARY.md 'chapters/foreword.md'
check_contains editions/en/content/SUMMARY.md 'chapters/foreword-to-the-french-edition.md'
check_contains editions/en/content/SUMMARY.md 'chapters/list-of-equations.md'
check_contains editions/fr/content/SUMMARY.md 'chapters/list-of-equations.md'
check_order editions/en/content/SUMMARY.md 'chapters/abbreviations-acronyms-and-abbreviations.md' 'chapters/foreword.md'
check_order editions/en/content/SUMMARY.md 'chapters/list-of-tables.md' 'chapters/list-of-equations.md'
check_order editions/fr/content/SUMMARY.md 'chapters/list-of-tables.md' 'chapters/list-of-equations.md'
check_order editions/en/content/SUMMARY.md 'chapters/foreword.md' 'chapters/foreword-to-the-french-edition.md'
check_order editions/en/content/SUMMARY.md 'chapters/foreword-to-the-french-edition.md' 'chapters/chapter-01-general-introduction.md'
check_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-001.webp'
check_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-002.webp'
check_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-003.webp'
check_not_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-001.png'
check_not_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-002.png'
check_not_contains editions/en/content/chapters/chapter-01-general-introduction.md 'figure-003.png'
for figure in 005 006 007 008 009 010 011 012 013 014; do
  check_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md "figure-${figure}.webp"
  check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md "figure-${figure}.png"
done
check_order editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-006.webp' 'figure-007.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-005-upstream-phases-transparent.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-006-block-assignment-transparent.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-010-em.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-011-system.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-012-geoseismic.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-013-anticline.webp'
check_not_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'figure-014-traps.webp'
for figure in 015 016 017 018 019 020 021 022 023 024 025 026 027 028 029 030 031 032; do
  check_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md "figure-${figure}.webp"
  check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md "figure-${figure}.png"
done
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-017.svg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-018.jpg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-019.svg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-022.svg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-023.svg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-026.svg'
check_not_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'figure-030.svg'
check_contains editions/en/content/SUMMARY.md 'chapters/cover.md'
check_contains editions/en/content/chapters/cover.md 'figure-000.webp'
check_not_contains editions/en/content/chapters/cover.md 'figure-001.webp'
check_contains editions/fr/content/SUMMARY.md 'chapters/cover.md'
check_contains editions/fr/content/chapters/cover.md 'figure-000.webp'
check_not_contains editions/fr/content/chapters/cover.md 'figure-001.webp'
check_contains public/book/index.html 'class="book-cover"'
check_contains public/book/index.html 'class="book-cover-frame"'
check_contains public/book/index.html 'class="book-cover-kicker"'
check_contains public/book/index.html 'class="book-cover-title"'
check_contains public/book/index.html 'class="book-cover-subtitle"'
check_contains public/book/index.html 'class="book-cover-figure"'
check_contains public/book/index.html 'class="book-cover-footer"'
check_contains public/book/index.html 'class="book-cover-imprint"'
check_contains public/book/index.html 'class="book-cover-entry"'
check_contains public/book/index.html 'class="book-cover-entry-link"'
check_contains public/book/index.html 'Start reading'
check_contains public/book/index.html 'class="book-cover-entry-link"'
check_contains public/book/index.html 'src="images/figure-000.webp"'
check_contains public/book/index.html 'href="chapters/disclaimer.html"'
check_contains public/book/index.html 'href="./"'
check_not_contains public/book/index.html 'href="index.html"'
check_not_contains public/book/index.html 'href="chapters/cover.html"'
check_not_contains public/book/index.html 'src="../images/figure-001.webp"'
check_not_contains public/book/index.html 'src="images/figure-001.webp"'
check_not_contains public/book/index.html 'href="../chapters/foreword.html"'
check_contains public/fr/book/index.html 'src="images/figure-000.webp"'
check_not_contains public/fr/book/index.html 'src="images/figure-001.webp"'
check_contains public/fr/book/chapters/list-of-figures.html 'href="../"'
check_not_contains public/fr/book/chapters/list-of-figures.html 'href="../index.html"'
check_not_contains public/fr/book/chapters/list-of-figures.html 'href="cover.html"'
check_contains public/book/index.html 'class="book-layout-booting book-page-cover"'
check_contains public/book/chapters/list-of-figures.html 'book-page-front-matter-outline-rail'
check_contains public/book/chapters/list-of-figures.html 'book-page-figure-index'
check_contains public/book/chapters/list-of-figures.html 'book-page-aux-index'
for book_theme_custom_js in public/book/theme/custom-*.js public/fr/book/theme/custom-*.js; do
  check_not_contains "$book_theme_custom_js" 'window.bookPageVariants'
  check_not_contains "$book_theme_custom_js" 'function applyPageVariants()'
  check_not_contains "$book_theme_custom_js" 'const englishDefaultChapterPath = "chapters/disclaimer.html";'
  check_not_contains "$book_theme_custom_js" 'const frenchDefaultChapterPath = "chapters/foreword.html";'
  check_not_contains "$book_theme_custom_js" 'new URL(getDefaultChapterPath(window.location.pathname), window.location.href)'
  check_not_contains "$book_theme_custom_js" 'window.location.replace(target.href)'
done
check_contains public/book/chapters/front-matter.html 'http-equiv="refresh"'
check_contains public/book/chapters/front-matter.html 'url=../'
check_contains public/book/chapters/front-matter.html 'window.location.replace(target)'
check_contains public/book/chapters/chapter-01-general-introduction.html 'figure-001.webp'
check_contains public/book/chapters/chapter-01-general-introduction.html 'figure-002.webp'
check_contains public/book/chapters/chapter-01-general-introduction.html 'figure-003.webp'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'figure-001.png'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'figure-002.png'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'figure-003.png'
for figure in 005 006 007 008 009 010 011 012 013 014; do
  check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html "figure-${figure}.webp"
  check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html "figure-${figure}.png"
done
check_order public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-006.webp' 'figure-007.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-005-upstream-phases-transparent.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-006-block-assignment-transparent.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-010-em.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-011-system.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-012-geoseismic.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-013-anticline.webp'
check_not_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'figure-014-traps.webp'
for figure in 015 016 017 018 019 020 021 022 023 024 025 026 027 028 029 030 031 032; do
  check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html "figure-${figure}.webp"
  check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html "figure-${figure}.png"
done
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-017.svg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-018.jpg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-019.svg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-022.svg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-023.svg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-026.svg'
check_not_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'figure-030.svg'
check_contains public/book/index.html 'Exploration and Exploitation of Petroleum Resources in West Africa'
check_contains public/book/index.html 'Exploration and Production of Petroleum Resources in West Africa'
check_contains public/book/index.html 'Upstream Atlas Reference Edition'
check_contains public/book/index.html 'Digital Reading Edition'
check_file_size_at_most public/book/images/figure-017.webp 5000000
check_file_size_at_least public/book/images/figure-011.webp 1
check_not_exists public/book/images/figure-018.jpg
check_not_exists public/fr/book/images/figure-018.jpg
check_contains public/book/chapters/list-of-figures.html 'List of Figures'
check_contains public/book/chapters/list-of-figures.html 'class="reference-index reference-index-figures"'
check_contains public/book/chapters/list-of-figures.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/list-of-figures.html 'chapter-01-general-introduction.html#figure-1'
check_contains public/book/chapters/list-of-figures.html 'chapter-08-west-african-fiscal-regimes.html#figure-79'
check_contains public/book/chapters/table-of-contents.html 'Table of Contents'
check_contains public/book/chapters/table-of-contents.html 'class="reference-index reference-index-toc"'
check_contains public/book/chapters/table-of-contents.html '<h2>Chapter 1: General Introduction</h2>'
check_contains public/book/chapters/table-of-contents.html 'class="reference-index-link" href="chapter-01-general-introduction.html#11--hydrocarbon-resources-and-economic-development">1.1 Hydrocarbon Resources and Economic Development</a>'
check_contains public/book/chapters/table-of-contents.html 'class="reference-index-link" href="chapter-08-west-african-fiscal-regimes.html#84--state-contractor-cash-flow-analysis">8.4 State-Contractor Cash Flow Analysis</a>'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-heading-link'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-heading-page'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-list--toc'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-toc-link'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-toc-label'
check_not_contains public/book/chapters/table-of-contents.html 'reference-index-toc-title'
check_not_contains public/book/chapters/table-of-contents.html '<p>1.General Introduction23</p>'
check_contains public/book/chapters/table-of-contents.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/table-of-contents.html 'class="chapter-nav-card chapter-nav-next"'
check_not_contains public/book/chapters/preface.html '1.General Introduction23'
check_not_contains public/book/chapters/preface.html 'Figure 1 African Petroleum Development Paradox'
check_not_contains public/book/chapters/preface.html 'Table 11 Summary of Ad Valorem Royalty Rates Applied in Selected West African Countries.'
check_not_contains public/book/chapters/preface.html 'AFREC'
check_not_contains public/book/chapters/preface.html 'African Energy Commission'
check_contains public/book/chapters/list-of-tables.html 'List of Tables'
check_contains public/book/chapters/list-of-tables.html 'class="reference-index reference-index-tables"'
check_contains public/book/chapters/list-of-tables.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/list-of-tables.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/list-of-tables.html 'chapter-05-hydrocarbon-value-chain.html#table-2'
check_contains public/book/chapters/list-of-tables.html 'chapter-08-west-african-fiscal-regimes.html#table-11'
check_contains public/book/chapters/list-of-equations.html 'List of Equations'
check_contains public/book/chapters/list-of-equations.html 'class="reference-index reference-index-equations"'
check_contains public/book/chapters/list-of-equations.html 'chapter-06-upstream-operations-and-government-roles.html#formula-6-1'
check_contains public/book/chapters/list-of-equations.html 'chapter-08-west-african-fiscal-regimes.html#formula-8-3'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'Abbreviations, Initialisms and Acronyms'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'AFREC'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'African Energy Commission'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/foreword.html 'Foreword to the English Edition'
check_contains public/book/chapters/foreword.html 'This English edition is based on the original French-language work authored by Charles'
check_contains public/book/chapters/foreword.html 'href="/fr/book/?lang=fr"'
check_contains public/book/chapters/foreword.html '<strong>Matthew</strong><br />'
check_contains public/book/chapters/foreword.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/foreword.html 'class="chapter-nav-card chapter-nav-next"'
check_not_contains public/book/chapters/foreword.html 'Geo-extractive resources are a source of income for countries'
check_contains public/book/chapters/foreword-to-the-french-edition.html 'Foreword to the French Edition'
check_contains public/book/chapters/foreword-to-the-french-edition.html 'Geo-extractive resources constitute an important source of revenue for countries endowed with them'
check_contains public/book/chapters/foreword-to-the-french-edition.html 'href="/fr/book/chapters/foreword.html?lang=fr"'
check_contains public/book/chapters/foreword-to-the-french-edition.html '<strong>Charles</strong><br />'
check_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md '<table>'
check_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'Crude Oil Reserves (MMbbl)'
check_contains editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md 'Reference Period'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '<table>'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '<thead>'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html '<tbody>'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'Crude Oil Reserves (MMbbl)'
check_contains public/book/chapters/chapter-05-hydrocarbon-value-chain.html 'Reference Period'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md '<table>'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'Table 20 Principal Fiscal Elements'
check_not_contains editions/en/content/chapters/chapter-04-national-oil-companies-in-west-africa.md 'Table 1 Overview of National Oil Companies in West Africa 175'
check_not_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md '&amp;amp;'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '<table>'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '<thead>'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '<tbody>'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'Table 20 Principal Fiscal Elements'
check_not_contains public/book/chapters/chapter-04-national-oil-companies-in-west-africa.html 'Table 1 Overview of National Oil Companies in West Africa 175'
check_not_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '&amp;amp;'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'Table 11 Summary of Ad Valorem Royalty Rates Applied in Selected West African Countries.'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'Table 12 Summary of Profit Oil Sharing Mechanisms and Government Profit Oil Entitlements in Selected West African Countries.'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '<p>Table 11 Summary of Ad Valorem Royalty Rates Applied in Selected West African Countries.</p>'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html '<p>Table 12 Summary of Profit Oil Sharing Mechanisms and Government Profit Oil Entitlements in Selected West African Countries.</p>'
check_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'data-equation-label="6.1"'
check_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'data-equation-label="6.2"'
check_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'data-equation-label="6.3"'
check_contains editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md 'class="formula-group formula-group--volumetric"'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'data-equation-label="8.1"'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'data-equation-label="8.2"'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'data-equation-label="8.3"'
check_contains editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md 'class="table-12-h-factor-cell"'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'data-equation-label="6.1"'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'data-equation-label="6.2"'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'data-equation-label="6.3"'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'class="formula-group formula-group--volumetric"'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'VHcP = GRV × N/G × ϕ × Shc × 1/FVF'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'FVF = Reservoir Volume / Surface Volume'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'STOIIP = GRV × N/G × ϕ × So × 1/Bo'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'GIIP = GRV × N/G × ϕ × Sg × 1/Bg'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html 'GCoS = Ps × Pr × Pse × Pt'
check_contains public/book/chapters/chapter-06-upstream-operations-and-government-roles.html '= 0.55 (55%)'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'data-equation-label="8.1"'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'data-equation-label="8.2"'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'data-equation-label="8.3"'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'class="book-formula-bridge">or<'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'H = 1.626'
check_contains theme/custom.css '#table-12 .table-12-h-factor-cell > .book-formula {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const formulaBlock=css.match(/#table-12 \.table-12-h-factor-cell > \.book-formula \{[^}]*\}/);const lineBlock=css.match(/#table-12 \.table-12-h-factor-cell > \.book-formula \.book-formula-line \{[^}]*\}/);if(!formulaBlock||!lineBlock){console.error("Expected Table 12 H-factor formula rule blocks.");process.exit(1);}for(const expected of ["width: 100%;","max-width: none;","overflow-x: visible;","white-space: normal;"]){if(!formulaBlock[0].includes(expected)){console.error(`Expected Table 12 H-factor formula block to include ${expected}`);process.exit(1);}}if(formulaBlock[0].includes("width: max-content;")){console.error("Expected Table 12 H-factor formula block to stop using width: max-content.");process.exit(1);}for(const expected of ["width: 100%;","min-width: 0;","white-space: normal;"]){if(!lineBlock[0].includes(expected)){console.error(`Expected Table 12 H-factor formula line block to include ${expected}`);process.exit(1);}}'
check_contains public/book/chapters/glossary.html '<strong>API Gravity</strong>'
check_contains public/book/chapters/glossary.html 'Light oil: &gt;30° API'
check_contains public/book/chapters/glossary.html 'Medium oil: 20-30° API'
check_contains public/book/chapters/glossary.html 'Heavy oil: 10-20° API'
check_contains public/book/chapters/glossary.html 'Extra-heavy oil: &lt;10° API'
check_not_contains public/book/chapters/glossary.html 'class="book-formula api-density-formula"'
check_not_contains public/book/chapters/glossary.html 'language-math'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'data-equation-label="2.1"'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'data-equation-label="2.2"'
check_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-001.webp'
check_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003.webp'
check_not_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-001-chain.webp'
check_not_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003.jpg'
check_not_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003-map.jpg'
check_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-004.webp'
check_not_contains editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-004.png'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-005.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-006.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-008.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-009.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-010.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-011.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-012.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-013.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-014.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-015.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-a.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-b.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-018.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-010-em.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-005.png'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-006.png'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-008.png'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-009.png'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-010.png'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-011-system.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-012-geoseismic.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-013-anticline.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-014-traps.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-015-depth-map.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-a.jpg'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-b.jpg'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-018-model.webp'
check_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-019.webp'
check_not_contains editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-019.svg'
check_contains editions/fr/content/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'data-equation-label="4.1"'
check_contains editions/fr/content/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'data-equation-label="4.2"'
check_contains editions/fr/content/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'data-equation-label="4.3"'
check_contains editions/fr/content/chapters/glossary.md 'class="book-formula api-density-formula"'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-group formula-group--prospect" data-equation-label="2.1"'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-group formula-group--volumetric" data-equation-label="2.2"'
check_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-001.webp'
check_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003.webp'
check_not_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-001-chain.webp'
check_not_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003.jpg'
check_not_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003-map.jpg'
check_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-004.webp'
check_not_contains public/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-004.png'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-005.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-006.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-008.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-009.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-010.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-011.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-012.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-013.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-014.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-015.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-a.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-b.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-018.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-010-em.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-005.png'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-006.png'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-008.png'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-009.png'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-010.png'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-011-system.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-012-geoseismic.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-013-anticline.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-014-traps.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-015-depth-map.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-a.jpg'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-b.jpg'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-018-model.webp'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-019.webp'
check_not_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-019.svg'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">Pour l’huile'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">Pour le gaz'
check_contains public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-connector">Ainsi,'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/fr/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html","utf8");const normalize=(value)=>value.replace(/<[^>]+>/g," ").replace(/&nbsp;/g," ").replace(/\u00a0/g," ").replace(/&minus;/g,"-").replace(/[−–]/g,"-").replace(/&times;/g,"x").replace(/&deg;/g,"°").replace(/\s+/g," ").trim();const text=normalize(html);const labels=[...html.matchAll(/data-equation-label=\"([^\"]+)\"/g)].map((match)=>match[1]);if(labels.join(",")!=="2.1,2.2"){console.error(`Expected French chapter 2 primary equation labels 2.1,2.2 but found ${labels.join(",")}`);process.exit(1);}for(const expected of ["P(prospect) = P(roche mère) x P(réservoir) x P(piège)","VHcP = GRV x N/G x Ø x Shc x 1/FVF","FVF = Volume réservoir/Volume à la surface"]){if(!text.includes(expected)){console.error(`Expected French chapter 2 formula content for: ${expected}`);process.exit(1);}}'
check_contains public/fr/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html '<div class="book-formula" data-equation-label="4.1"'
check_contains public/fr/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="formula-group formula-group--split formula-group--oil-profit" data-equation-label="4.2"'
check_contains public/fr/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="formula-panel formula-panel--r-factor" data-equation-label="4.3"'
check_contains public/fr/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="book-formula-bridge">ou<'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/fr/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html","utf8");const normalize=(value)=>value.replace(/<[^>]+>/g," ").replace(/&nbsp;/g," ").replace(/\u00a0/g," ").replace(/&minus;/g,"-").replace(/[−–]/g,"-").replace(/&times;/g,"x").replace(/&deg;/g,"°").replace(/\s+/g," ").trim();const text=normalize(html);const labels=[...html.matchAll(/data-equation-label=\"([^\"]+)\"/g)].map((match)=>match[1]);if(labels.join(",")!=="4.1,4.2,4.3"){console.error(`Expected French chapter 4 primary equation labels 4.1,4.2,4.3 but found ${labels.join(",")}`);process.exit(1);}for(const expected of ["Revenu Post Royalty = Revenu brut - Royalty","Pétrole profit = Revenue post Royalty - Coûts récupérables","Facteur-R=Revenu net cumulé/Coûts cumulés"]){if(!text.includes(expected)){console.error(`Expected French chapter 4 formula content for: ${expected}`);process.exit(1);}}'
check_contains public/fr/book/chapters/glossary.html 'class="book-formula api-density-formula"'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/fr/book/chapters/glossary.html","utf8");if(!/Densité\s*API\s*=/.test(html)||!/Densité\s*à\s*15°C/.test(html)||!html.includes("141.5")||!html.includes("131.5")||html.includes("API density")){console.error("Expected French glossary formula to use French density terms and decimal points");process.exit(1);}'
check_contains public/book/toc.html 'List of Figures'
check_contains public/book/toc.html 'List of Tables'
check_not_contains public/book/toc.html 'Abbreviations, Acronyms and Abbreviations'
check_not_contains public/book/toc.html 'href="chapters/cover.html"'
check_not_contains public/fr/book/toc.html 'href="chapters/cover.html"'
for raw_toc_script in public/book/toc-*.js public/fr/book/toc-*.js; do
  check_not_contains "$raw_toc_script" 'href="chapters/cover.html"'
done
check_not_contains public/book/index.html 'site-footer-detailed'
check_not_contains public/book/chapters/chapter-01-general-introduction.html 'site-footer-detailed'
check_contains public/book/index.html 'upstream-atlas-favicon.png?v=2'
check_not_contains public/book/index.html 'fonts.googleapis.com'
check_not_contains public/book/index.html 'fonts.gstatic.com'

# Reader shell contract
check_contains public/book/index.html 'rel="preload" href="reader-fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin'
check_contains public/book/index.html 'rel="preload" href="reader-fonts/literata-var.woff2" as="font" type="font/woff2" crossorigin'
check_exists public/book/reader-fonts/inter-var.woff2
check_exists public/book/reader-fonts/literata-var.woff2
check_not_contains public/book/index.html 'favicon-de23e50b.svg'
check_not_contains public/book/index.html 'favicon-8114d1fc.png'
check_not_contains public/book/index.html 'class="book-home-label"'
check_not_contains public/book/index.html 'Upstream Atlas</span>'
check_contains theme/custom.css '@font-face {'
check_contains theme/custom.css 'font-family: "Inter";'
check_contains theme/custom.css 'url("../reader-fonts/inter-var.woff2") format("woff2");'
check_contains theme/custom.css 'font-family: "Literata";'
check_contains theme/custom.css 'url("../reader-fonts/literata-var.woff2") format("woff2");'
check_contains theme/custom.css 'font-display: block;'
check_contains theme/custom.css '--reader-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;'
check_contains theme/custom.css '--reader-serif: "Literata", Georgia, serif;'
check_contains theme/custom.css '--menu-bar-height: 56px;'
check_contains theme/custom.css '.reader-article {'
check_contains theme/custom.css '.reader-article blockquote {'
check_contains theme/custom.css 'font-family: var(--reader-serif);'
check_contains theme/custom.css 'color: var(--ink);'
check_contains theme/custom.css '.reader-article p,'
check_contains theme/custom.css '.reader-article li {'
check_contains theme/custom.css 'color: var(--ink);'
check_contains theme/custom.css '--reader-left-offset: 0px;'
check_contains theme/custom.css '--sidebar-scroll-padding-block: 1.8rem;'
check_contains theme/custom.css '--toolbar-search-width: 420px;'
check_contains theme/custom.css '--toolbar-contact-width: 106px;'
check_contains theme/custom.css '--toolbar-utility-gap: 24px;'
check_contains theme/custom.css '--reader-dek-measure: 44rem;'
check_contains theme/custom.css '--reader-figure-max-width: var(--content-max-width);'
check_contains theme/custom.css '--reader-table-max-width: var(--content-max-width);'
check_contains theme/custom.css '.book-toolbar {'
check_contains theme/custom.css 'display: grid;'
check_contains theme/custom.css 'grid-template-columns: var(--sidebar-width) minmax(0, 1fr) auto;'
check_contains theme/custom.css 'padding: 0;'
check_contains theme/custom.css '.toolbar-sidebar,'
check_contains theme/custom.css '.toolbar-main,'
check_contains theme/custom.css '.toolbar-actions {'
check_contains theme/custom.css '.toolbar-sidebar {'
check_contains theme/custom.css 'width: var(--sidebar-width);'
check_contains theme/custom.css 'justify-content: flex-start;'
check_contains theme/custom.css '.toolbar-main {'
check_contains theme/custom.css 'position: static;'
check_contains theme/custom.css 'padding-inline: 1.5rem 1rem;'
check_contains theme/custom.css 'pointer-events: auto;'
check_contains theme/custom.css '.toolbar-main .toolbar-search-slot {'
check_contains theme/custom.css 'width: min(100%, var(--toolbar-search-width));'
check_contains theme/custom.css 'max-width: var(--toolbar-search-width);'
check_contains theme/custom.css 'margin-inline: auto;'
check_contains theme/custom.css 'pointer-events: auto;'
check_contains theme/custom.css '.toolbar-actions {'
check_contains theme/custom.css 'justify-content: flex-end;'
check_contains theme/custom.css 'min-width: calc(var(--toolbar-contact-width) + 1rem);'
check_contains theme/custom.css 'padding-inline-end: 24px;'
check_contains theme/custom.css '.toolbar-contact-link {'
check_contains theme/custom.css 'width: auto !important;'
check_contains theme/custom.css 'min-height: 36px;'
check_contains theme/custom.css '.toolbar-actions .toolbar-contact-link {'
check_contains theme/custom.css '.toolbar-line-icon {'
check_contains theme/custom.css 'width: 20px;'
check_contains theme/custom.css 'height: 20px;'
check_contains theme/custom.css '.toolbar-line-icon svg {'
check_contains theme/custom.css 'stroke-width: 1.8;'
check_contains theme/custom.css 'stroke-linecap: round;'
check_contains theme/custom.css 'stroke-linejoin: round;'
check_contains theme/custom.css '.toolbar-contact-link .toolbar-line-icon {'
check_contains theme/custom.css 'transform: translateY(0.25px);'
check_contains theme/custom.css '.toolbar-link-label {'
check_contains theme/custom.css 'font-size: 0.875rem;'
check_contains theme/custom.css '.book-home-icon {'
check_contains theme/custom.css 'gap: 1rem;'
check_contains theme/custom.css '.book-home-icon-full {'
check_contains theme/custom.css 'width: 138px;'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle {'
check_contains theme/custom.css 'width: 28px;'
check_contains theme/custom.css 'height: 28px;'
check_contains theme/custom.css 'flex: 0 0 28px;'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle .toolbar-line-icon-menu {'
check_contains theme/custom.css 'width: 16px;'
check_contains theme/custom.css 'height: 16px;'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle .toolbar-line-icon-menu svg {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const selector="#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle .toolbar-line-icon-menu svg {";const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);if(!block.includes("stroke-width: 2;")){console.error("Expected toggle menu icon stroke-width: 2;");process.exit(1);}'
check_contains theme/custom.css '.book-home-icon-compact {'
check_contains theme/custom.css 'width: 24px;'
check_contains theme/custom.css 'height: 24px;'
check_contains theme/custom.css '.book-cover-entry {'
check_not_contains theme/custom.css 'body.book-page-aux-index .chapter-pagination {'
check_contains theme/custom.css '@media (max-width: 1023px) {'
check_not_contains theme/custom.css '.book-home-label {'
check_contains theme/custom.css '.toolbar-search-slot {'
check_contains theme/custom.css '.toolbar-search-slot.hidden {'
check_contains theme/custom.css 'width: min(100%, var(--toolbar-search-width));'
check_contains theme/custom.css 'max-width: var(--toolbar-search-width);'
check_contains theme/custom.css '.toolbar-search-slot.is-focused {'
check_contains theme/custom.css '.toolbar-search-slot #mdbook-searchbar-outer {'
check_contains theme/custom.css '.search-clear-button {'
check_contains theme/custom.css '.toolbar-search-slot .searchresults-outer {'
check_contains theme/custom.css '.toolbar-search-slot #mdbook-searchbar {'
check_contains theme/custom.css '#mdbook-searchbar::placeholder {'
check_contains theme/custom.css '#mdbook-searchbar::-webkit-search-cancel-button {'
check_contains theme/custom.css '.toolbar-actions .toolbar-contact-link:hover,'
check_contains theme/custom.css '#mdbook-search-toggle {'
check_contains theme/custom.css 'position: absolute;'
check_contains theme/custom.css 'inset-inline: 0;'
check_contains theme/custom.css 'top: calc(100% + 8px);'
check_contains theme/custom.css 'max-height: min(65vh, 34rem);'
check_contains theme/custom.css '.search-result-icon {'
check_contains theme/custom.css '.search-empty-state {'
check_contains theme/custom.css '@media (max-width: 1280px) {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const searchbar=block(".toolbar-search-slot #mdbook-searchbar {");for(const expected of ["background: rgba(255, 255, 255, 0.94);","border: 1px solid rgba(17, 35, 63, 0.08);","box-shadow: 0 10px 22px rgba(15, 31, 58, 0.08);","color: var(--ink);"]){if(!searchbar.includes(expected)){console.error(`Expected .toolbar-search-slot #mdbook-searchbar to include ${expected}`);process.exit(1);}}const placeholder=block("#mdbook-searchbar::placeholder {");for(const expected of ["color: rgba(11, 31, 51, 0.52);","opacity: 1;"]){if(!placeholder.includes(expected)){console.error(`Expected #mdbook-searchbar::placeholder to include ${expected}`);process.exit(1);}}const contact=block(".toolbar-actions .toolbar-contact-link {");for(const expected of ["color: rgba(11, 31, 51, 0.72);"]){if(!contact.includes(expected)){console.error(`Expected .toolbar-actions .toolbar-contact-link to include ${expected}`);process.exit(1);}}const contactHover=block(".toolbar-actions .toolbar-contact-link:hover,");for(const expected of ["color: var(--brand-blue-deep);","background: rgba(49, 99, 194, 0.06);"]){if(!contactHover.includes(expected)){console.error(`Expected .toolbar-actions .toolbar-contact-link:hover, to include ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar .icon-button,'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar .toolbar-link {'
check_contains theme/custom.css 'display: inline-flex;'
check_contains theme/custom.css 'justify-content: center;'
check_contains theme/custom.css 'width: 36px;'
check_contains theme/custom.css 'height: 36px;'
check_contains theme/custom.css 'flex: 0 0 36px;'
check_contains theme/custom.css 'line-height: 1;'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar .fa-svg,'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar .icon-button .fa-svg,'
check_contains theme/custom.css '#mdbook-menu-bar .book-toolbar .toolbar-link .fa-svg {'
check_contains theme/custom.css 'display: block;'
check_contains theme/custom.css 'width: 20px;'
check_contains theme/custom.css 'height: 20px;'
check_contains theme/custom.css 'pointer-events: none;'
check_contains theme/custom.css '.reader-layout {'
check_contains theme/custom.css '--outline-width: 256px;'
check_contains theme/custom.css 'grid-template-columns: minmax(0, 1fr) var(--outline-width);'
check_contains theme/custom.css '.book-sidebar-shell {'
check_contains theme/custom.css '.book-sidebar-intro {'
check_not_contains theme/custom.css '.book-sidebar-utility-nav {'
check_not_contains theme/custom.css '.book-sidebar-utility-link {'
check_not_contains theme/custom.css '--sidebar-intro-height:'
check_not_contains theme/custom.css '--sidebar-utilities-height:'
check_contains theme/custom.css '.reader-sidebar-scroll {'
check_contains theme/custom.css '.reader-sidebar-projection {'
check_contains theme/custom.css '.reader-sidebar-section {'
check_contains theme/custom.css '.reader-sidebar-section-header {'
check_contains theme/custom.css '.reader-sidebar-section-body {'
check_contains theme/custom.css '.reader-sidebar-row {'
check_contains theme/custom.css '.reader-sidebar-row-index {'
check_contains theme/custom.css '.reader-sidebar-row-title {'
check_contains theme/custom.css '.reader-sidebar-row--active {'
check_contains theme/custom.css '.reader-sidebar-section--active::before {'
check_not_contains theme/custom.css '.book-sidebar-utility-link-icon {'
check_not_contains theme/custom.css '.book-sidebar-download {'
check_contains theme/custom.css '--sidebar-width: 256px;'
check_contains theme/custom.css 'top: var(--menu-bar-height);'
check_contains theme/custom.css '@media (min-width: 1024px) {'
check_contains theme/custom.css '--sidebar-width: 320px;'
check_contains theme/custom.css '--content-max-width: 896px;'
check_contains theme/index.hbs "shim.id = 'mdbook-sidebar-resize-handle';"
check_contains theme/index.hbs "shim.style.display = 'none';"
check_contains theme/index.hbs '<button id="mdbook-theme-toggle" type="button" tabindex="-1"></button>'
check_contains theme/index.hbs '<ul id="mdbook-theme-list" class="theme-popup" aria-label="Themes" role="menu">'
check_contains theme/index.hbs '<div id="mdbook-search-overlay-root" aria-hidden="true"></div>'
check_contains theme/index.hbs '<div id="mdbook-search-wrapper" class="hidden">'
check_contains theme/index.hbs '<button id="mdbook-search-clear" class="search-clear-button" type="button" aria-label="Clear search" hidden>&times;</button>'
check_contains theme/index.hbs '<div class="toolbar-search-slot hidden" aria-hidden="true"></div>'
check_contains theme/index.hbs '<button id="mdbook-search-toggle" class="icon-button" type="button" title="Search (`/`)" aria-label="Toggle Searchbar" aria-expanded="false" aria-keyshortcuts="/ s" aria-controls="mdbook-searchbar">'
check_not_contains theme/index.hbs '<script src="{{ resource "searcher.js" }}"></script>'
check_contains theme/index.hbs 'class="book-sidebar-intro"'
check_not_contains theme/index.hbs 'Reader Edition'
check_contains theme/index.hbs 'class="reader-sidebar-scroll"'
check_contains theme/index.hbs 'class="reader-sidebar-projection"'
check_not_contains theme/index.hbs 'class="book-sidebar-utilities"'
check_not_contains theme/index.hbs 'class="book-sidebar-utility-link-icon"'
check_not_contains theme/index.hbs 'Reference Surfaces'
check_not_contains theme/index.hbs 'class="book-sidebar-download"'
check_contains theme/index.hbs 'class="toolbar-link-label"'
check_not_contains theme/index.hbs 'reader-mobile-chapter-bar'
check_not_contains theme/index.hbs 'reader-mobile-chapter-toggle'
check_contains theme/index.hbs 'class="reader-chapter-hero-anchor"'
check_contains theme/index.hbs 'class="reader-mobile-outline-anchor"'
check_contains theme/index.hbs 'class="book-outline-section book-outline-figures"'
check_contains theme/index.hbs 'class="book-outline-section book-outline-tables"'
check_contains theme/index.hbs 'class="book-outline-section book-outline-formulas"'
check_not_contains theme/index.hbs 'function applyInitialBookPageVariant()'
node -e 'const fs=require("fs");const text=fs.readFileSync("scripts/test-site-render.sh","utf8");const legacy=["/book ","62.5%"," root contract"].join("");if(text.includes(legacy)){console.error("Expected scripts/test-site-render.sh to stop referring to the legacy /book root contract in test messages");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");if(!/:root\s*\{[^}]*font-size:\s*100%;/s.test(css)){console.error("Expected theme/custom.css to declare the repo-owned /book root font-size: 100%");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const rootMatch=css.match(/:root\s*\{[\s\S]*?\n\}/);if(!rootMatch){console.error("Expected :root block in theme/custom.css");process.exit(1);}for(const expected of ["--reader-ink: #0b1f33;","--reader-muted: #526171;","--reader-brand: #3163c2;","--reader-brand-deep: #264d97;","--reader-sidebar-width: 320px;","--reader-sidebar-width-base: 256px;","--reader-outline-width: 256px;","--reader-content-max: 896px;","--reader-logo-width-desktop: 138px;","--reader-logo-width-narrow: 180px;","--reader-figure-radius: 20px;","--reader-table-radius: 16px;","--reader-formula-radius: 6px;"]){if(!rootMatch[0].includes(expected)){console.error(`Expected :root token mapping for ${expected}`);process.exit(1);}}'
node <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");

function block(selector) {
  const start = css.indexOf(selector);
  if (start === -1) {
    console.error(`Expected selector block: ${selector}`);
    process.exit(1);
  }

  const end = css.indexOf("}", start);
  if (end === -1) {
    console.error(`Expected closing brace for selector block: ${selector}`);
    process.exit(1);
  }

  return css.slice(start, end + 1);
}

const expectations = [
  [".book-sidebar-intro {", ["padding: 1.55rem 1.75rem 1.05rem;", "border-bottom: 0;"]],
  [".book-sidebar-intro::after {", ["inset-inline: 0;", "border-bottom: 1px solid rgba(11, 31, 51, 0.08);"]],
  [".book-sidebar-book-title {", ["font-family: var(--reader-sans);", "max-width: 24ch;", "font-size: 0.9rem;", "font-weight: 600;", "line-height: 1.38;", "text-transform: uppercase;"]],
  [".reader-sidebar-scroll {", ["padding: var(--sidebar-scroll-padding-block) 1rem 1rem;", "overflow-y: auto;"]],
  [".reader-sidebar-projection {", ["width: 100%;", "box-sizing: border-box;"]],
  [".reader-sidebar-section {", ["position: relative;", "grid-template-columns: minmax(0, 1fr);", "gap: 0.4rem;", "width: 100%;", "padding-top: 2.4rem;", "padding-inline: 0.75rem;", "border-top: 0;", "box-sizing: border-box;"]],
  [".reader-sidebar-section::before {", ["inset-inline: 0;", "border-top: 1px solid rgba(11, 31, 51, 0.08);"]],
  [".reader-sidebar-section:first-child::before {", ["content: none;"]],
  [".reader-sidebar-section--active::before {", ["border-top-color: rgba(49, 99, 194, 0.2);"]],
  [".reader-sidebar-section-header {", ["gap: 0.2rem;", "align-items: start;"]],
  [".reader-sidebar-section-kicker {", ["font-size: 0.75rem;", "letter-spacing: 0.12em;"]],
  [".reader-sidebar-section-title {", ["font-size: 0.875rem;", "line-height: 1.35;"]],
  [".reader-sidebar-section-icon {", ["width: 1.1875rem;", "height: 1.1875rem;", "color: rgba(82, 97, 113, 0.88);"]],
  [".reader-sidebar-section--part {", ["gap: 0.8rem;"]],
  [".reader-sidebar-section--part .reader-sidebar-section-header {", ["display: block;"]],
  [".reader-sidebar-section--part .reader-sidebar-section-kicker {", ["display: inline;", "color: var(--brand-gold);", "font-size: 0.75rem;", "letter-spacing: normal;"]],
  [".reader-sidebar-section--part .reader-sidebar-section-title {", ["display: inline;", "color: var(--brand-gold);", "font-family: var(--reader-sans);", "font-size: 0.75rem;", "line-height: 1.35;", "text-transform: uppercase;"]],
  [".reader-sidebar-section--part .reader-sidebar-section-title::before {", ['content: "|";']],
  [".reader-sidebar-section--part.reader-sidebar-section--active .reader-sidebar-section-title {", ["color: var(--brand-gold);"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-section-header {", ["grid-template-columns: auto minmax(0, 1fr);", "align-items: center;", "column-gap: 0.625rem;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-section-title,", ["color: var(--sidebar-fg);", "font-family: var(--reader-sans);", "font-weight: 650;", "text-transform: none;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-section-body,", ["gap: 0.3rem;"]],
  [".reader-sidebar-section-body {", ["grid-template-columns: minmax(0, 1fr);", "gap: 0.35rem;", "width: 100%;", "padding-bottom: 0.75rem;", "box-sizing: border-box;"]],
  [".reader-sidebar-row {", ["grid-template-columns: 2.25rem minmax(0, 1fr);", "gap: 0.625rem;", "width: 100%;", "padding: 0.5rem 2rem 0.5rem 0.75rem;", "border-radius: 0.75rem;", "color: var(--sidebar-fg);", "box-sizing: border-box;"]],
  [".reader-sidebar-row-index {", ["color: currentColor;", "font-size: 0.6875rem;", "letter-spacing: 0.14em;"]],
  [".reader-sidebar-row-title {", ["display: block;", "width: 100%;", "font-family: var(--reader-sans);", "font-size: 0.8125rem;", "line-height: 1.45;"]],
  [".reader-sidebar-row--reference {", ["padding: 0.4rem 2rem 0.4rem 0.75rem;", "border-radius: 0.5rem;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-row--reference {", ["padding: 0.4rem 2rem 0.4rem calc(1.1875rem + 0.625rem);"]],
  [".reader-sidebar-row--reference.reader-sidebar-row--with-icon {", ["grid-template-columns: 1.375rem minmax(0, 1fr);", "gap: 0.5rem;"]],
  [".reader-sidebar-row--reference .reader-sidebar-row-title {", ["font-size: 0.8125rem;", "line-height: 1.45;"]],
  [".reader-sidebar-row-icon {", ["width: 1.375rem;", "height: 1.375rem;", "border-radius: 999px;"]],
  [".reader-sidebar-row:hover,", ["border-color: rgba(49, 99, 194, 0.12);", "background: rgba(49, 99, 194, 0.06);", "color: var(--sidebar-fg);"]],
  [".reader-sidebar-row--reference.reader-sidebar-row--active {", ["padding: 0.4rem 2rem 0.4rem 0.75rem;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-row--reference.reader-sidebar-row--active {", ["padding: 0.4rem 2rem 0.4rem calc(1.1875rem + 0.625rem);"]],
  [".reader-sidebar-row--active {", ["box-shadow: 0 8px 18px rgba(49, 99, 194, 0.14);"]],
  [".reader-sidebar-row--active:link,", ["color: #ffffff !important;", "-webkit-text-fill-color: #ffffff;"]],
  [".reader-sidebar-row--active .reader-sidebar-row-index,", ["color: #ffffff !important;", "-webkit-text-fill-color: #ffffff;"]],
  [".reader-sidebar-row--active .reader-sidebar-row-icon {", ["color: #ffffff;", "background: rgba(255, 255, 255, 0.14);"]],
  [".reader-sidebar-row--active::after {", ["inset-inline-end: 0.75rem;", "width: 0.4rem;", "height: 0.4rem;"]],
  [".reader-chapter-dek {", ["max-width: var(--reader-dek-measure);"]],
  [".figure-card {", ["width: min(100%, var(--reader-figure-max-width));"]],
  [".table-anchor-target {", ["width: min(100%, var(--reader-table-max-width));"]],
  [".book-outline-label {", ["font-size: 11px;", "letter-spacing: 0.16em;"]],
  [".book-outline-section-title {", ["font-size: 0.6875rem;", "letter-spacing: 0.16em;"]],
  [".book-outline-link--reference {", ["display: grid;", "grid-template-columns: auto minmax(0, 1fr);", "column-gap: 0.8rem;", "font-size: 0.8125rem;"]],
  [".book-outline-link--reference:visited {", ["font-size: 0.8125rem;", "line-height: 1.55;"]],
  [".reader-outline .book-outline-link--reference-label {", ["color: var(--links);", "white-space: nowrap;"]],
  [".reader-outline .book-outline-link--reference-title {", ["color: var(--ink);", "display: block;", "white-space: normal;"]],
  ["@media (min-width: 1024px) {", ["--sidebar-width: 320px;"]],
];

for (const [selector, declarations] of expectations) {
  const rule = block(selector);
  for (const declaration of declarations) {
    if (!rule.includes(declaration)) {
      console.error(`Expected ${selector} to include ${declaration}`);
      process.exit(1);
    }
  }
}
NODE
node <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");

function block(selector) {
  const start = css.indexOf(selector);
  if (start === -1) {
    console.error(`Expected selector block: ${selector}`);
    process.exit(1);
  }

  const end = css.indexOf("}", start);
  if (end === -1) {
    console.error(`Expected closing brace for selector block: ${selector}`);
    process.exit(1);
  }

  return css.slice(start, end + 1);
}

const shell = block(".book-sidebar-shell {");
const intro = block(".book-sidebar-intro {");
const resizeHandle = block(".book-sidebar-shell .sidebar-resize-handle {");

for (const [name, rule, required] of [
  [
    ".book-sidebar-shell {",
    shell,
    [
      "background: linear-gradient(180deg, rgba(252, 253, 255, 0.985) 0%, rgba(248, 250, 252, 0.96) 100%);",
      "box-shadow:",
      "inset -1px 0 0 rgba(15, 23, 42, 0.035);",
    ],
  ],
  [
    ".book-sidebar-intro {",
    intro,
    [
      "background: linear-gradient(180deg, rgba(255, 255, 255, 0.995) 0%, rgba(249, 250, 252, 0.98) 100%);",
    ],
  ],
  [
    ".book-sidebar-shell .sidebar-resize-handle {",
    resizeHandle,
    [
      "background-color: rgba(255, 255, 255, 0.96);",
    ],
  ],
]) {
  for (const expected of required) {
    if (!rule.includes(expected)) {
      console.error(`Expected ${name} to include ${expected}`);
      process.exit(1);
    }
  }
}

for (const [name, rule] of [
  [".book-sidebar-shell {", shell],
  [".book-sidebar-intro {", intro],
]) {
  if (rule.includes("background: var(--soft-blue);")) {
    console.error(`Expected ${name} to stop using the soft-blue solid sidebar surface`);
    process.exit(1);
  }
}
NODE
node <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");

function slice(startMarker, endMarker) {
  const start = css.indexOf(startMarker);
  const end = css.indexOf(endMarker, start);

  if (start === -1 || end === -1) {
    console.error(`Expected CSS slice between ${startMarker} and ${endMarker}`);
    process.exit(1);
  }

  return css.slice(start, end);
}

const mobileDrawer = slice("@media (max-width: 1080px) {", "@media (max-width: 760px) {");
const narrowHeader = slice("@media (max-width: 1023px) {", "@media (min-width: 768px) and (max-width: 1023px) {");

for (const expected of [
  "--sidebar-width: min(100vw, 40rem);",
  "#mdbook-sidebar-toggle-anchor:checked ~ #mdbook-sidebar {",
  "width: 100vw;",
  "max-width: 100vw;",
  "z-index: 24;",
  "background: linear-gradient(180deg, rgba(255, 255, 255, 0.998) 0%, rgba(248, 250, 252, 1) 100%);",
  "box-shadow: 18px 0 42px rgba(15, 23, 42, 0.16);",
  "#mdbook-sidebar-toggle-anchor:checked ~ #mdbook-page-wrapper {",
  "margin-left: 0;",
  "margin-inline-start: 0;",
  ".book-sidebar-intro {",
  "padding: 1.5rem 1.75rem 1rem;",
  ".book-sidebar-book-title {",
  "max-width: 24ch;",
  "font-size: 0.9rem;",
  "line-height: 1.38;",
  ".reader-sidebar-scroll {",
  "padding: 1rem 1.5rem 1.5rem;",
  ".reader-sidebar-section {",
  "gap: 0.75rem;",
  "padding-top: 1rem;",
  "padding-inline: 0.25rem;",
  "border-top: 0;",
  ".reader-sidebar-section::before {",
  "inset-inline: 0;",
  ".reader-sidebar-section-header {",
  "gap: 0.25rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-section-header {",
  "grid-template-columns: auto minmax(0, 1fr);",
  "column-gap: 0.625rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-section-title,",
  "font-size: 0.875rem;",
  "text-transform: none;",
  ".reader-sidebar-section--front-matter .reader-sidebar-section-body,",
  ".reader-sidebar-section--part .reader-sidebar-section-kicker {",
  "font-size: 0.75rem;",
  "letter-spacing: normal;",
  ".reader-sidebar-section--part .reader-sidebar-section-title {",
  "font-size: 0.8125rem;",
  "line-height: 1.32;",
  "max-width: 20ch;",
  ".reader-sidebar-section-body {",
  "gap: 0.5rem;",
  "padding-bottom: 0.875rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-section-body,",
  "gap: 0.25rem;",
  ".reader-sidebar-row {",
  "grid-template-columns: 2.25rem minmax(0, 1fr);",
  "gap: 0.625rem;",
  "padding: 0.5rem 2.125rem 0.5rem 0.75rem;",
  "border-radius: 0.75rem;",
  "color: var(--sidebar-fg);",
  ".reader-sidebar-row-index {",
  "font-size: 0.6875rem;",
  ".reader-sidebar-row-title {",
  "font-size: 0.875rem;",
  "line-height: 1.4;",
  "font-weight: 560;",
  ".reader-sidebar-row--reference {",
  "grid-template-columns: minmax(0, 1fr);",
  "padding: 0.4rem 2.125rem 0.4rem 0.75rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-row--reference {",
  "padding: 0.4rem 2.125rem 0.4rem calc(1.1875rem + 0.625rem);",
  ".reader-sidebar-row--reference.reader-sidebar-row--with-icon {",
  "grid-template-columns: 1.375rem minmax(0, 1fr);",
  "gap: 0.5rem;",
  ".reader-sidebar-row--reference .reader-sidebar-row-title {",
  "font-size: 0.8125rem;",
  "font-weight: 560;",
  ".reader-sidebar-row-icon {",
  "width: 1.375rem;",
  "height: 1.375rem;",
  ".reader-sidebar-row--reference.reader-sidebar-row--active {",
  "padding: 0.4rem 2.125rem 0.4rem 0.75rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-row--reference.reader-sidebar-row--active {",
  "padding: 0.4rem 2.125rem 0.4rem calc(1.1875rem + 0.625rem);",
  ".reader-sidebar-row--active {",
  "box-shadow: 0 8px 18px rgba(49, 99, 194, 0.16);",
  ".reader-sidebar-row--active::after {",
  "inset-inline-end: 0.9rem;",
  "width: 0.4rem;",
  "height: 0.4rem;",
]) {
  if (!mobileDrawer.includes(expected)) {
    console.error(`Expected mobile drawer CSS to include ${expected}`);
    process.exit(1);
  }
}

for (const expected of [
  ".book-toolbar {",
  "grid-template-columns: auto 1fr auto;",
  ".toolbar-actions {",
  "display: flex;",
  ".toolbar-main {",
  "position: absolute;",
  ".toolbar-main .toolbar-search-slot.hidden {",
  "display: none !important;",
  ".toolbar-actions .reader-language-switch[data-reader-language-switch=\"toolbar\"] {",
  "display: inline-flex;",
  "order: 1;",
  "font-size: 0.66rem;",
  "gap: 0.2rem;",
  "padding: 0.2rem 0.25rem;",
  ".toolbar-actions .reader-language-switch[data-reader-language-switch=\"toolbar\"] .reader-language-option {",
  "min-width: 1.55rem;",
  "min-height: 1.55rem;",
  "a.reader-language-option {",
  "position: relative;",
  "a.reader-language-option::before {",
  "content: \"\";",
  "width: 44px;",
  "height: 44px;",
  "#mdbook-menu-bar .book-toolbar .toolbar-actions .toolbar-contact-link {",
  "display: inline-flex !important;",
  "order: 2;",
  "width: 44px !important;",
  "height: 44px !important;",
  "padding: 0 !important;",
  "gap: 0;",
  ".toolbar-actions .toolbar-contact-link .toolbar-link-label {",
  "display: none;",
  "#mdbook-search-toggle {",
  "display: inline-flex !important;",
  "order: 3;",
  "width: 44px !important;",
  "height: 44px !important;",
  "flex: 0 0 44px !important;",
  "#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle {",
  "position: relative;",
  "width: 28px;",
  "height: 28px;",
  "flex: 0 0 28px;",
  "#mdbook-menu-bar .book-toolbar #mdbook-sidebar-toggle::before {",
  "content: \"\";",
  "width: 44px;",
  "height: 44px;",
  ".toolbar-sidebar {",
  "gap: 0.625rem;",
  "padding-inline-end: 0;",
  ".toolbar-actions {",
  "padding-inline-start: 0.5rem;",
  "gap: 0.5rem;",
  ".book-home-link {",
  "width: 44px;",
  "height: 44px;",
  "flex: 0 0 44px;",
  "justify-content: center;",
  ".book-home-icon-full {",
  "display: none;",
  ".book-home-icon-compact {",
  "display: block;",
  "width: 32px;",
  "height: 32px;",
]) {
  if (!narrowHeader.includes(expected)) {
    console.error(`Expected narrow-header CSS to include ${expected}`);
    process.exit(1);
  }
}
NODE

node - <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");
const marker = "@media (min-width: 768px) and (max-width: 1023px) {";
const start = css.indexOf(marker);
if (start === -1) {
  console.error("Expected tablet-specific toolbar logo media query.");
  process.exit(1);
}
const next = css.indexOf("\n\n@media", start + marker.length);
const block = (next === -1 ? css.slice(start) : css.slice(start, next));
for (const expected of [
  ".book-home-link {",
  "width: auto;",
  "height: 44px;",
  "flex: 0 0 auto;",
  ".book-home-icon-full {",
  "display: block;",
  "width: auto;",
  "height: 36px;",
  ".book-home-icon-compact {",
  "display: none;",
]) {
  if (!block.includes(expected)) {
    console.error(`Expected tablet toolbar logo CSS to include ${expected}`);
    process.exit(1);
  }
}
NODE

node - <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");
const marker = "@media (min-width: 1024px) {";
const start = css.lastIndexOf(marker);
if (start === -1) {
  console.error("Expected desktop-specific toolbar media query.");
  process.exit(1);
}
const next = css.indexOf("\n\n@media", start + marker.length);
const block = (next === -1 ? css.slice(start) : css.slice(start, next));
for (const expected of [
  ".book-home-icon-full {",
  "width: auto;",
  "height: 36px;",
]) {
  if (!block.includes(expected)) {
    console.error(`Expected desktop toolbar CSS to include ${expected}`);
    process.exit(1);
  }
}
NODE

node - <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");
const formulaRule = css.match(/\.formula-group--volumetric \.formula-case \.book-formula \{[\s\S]*?\n\}/);
if (!formulaRule) {
  console.error("Expected volumetric formula rule in theme/custom.css");
  process.exit(1);
}
for (const expected of [
  "width: 100%;",
  "overflow-x: auto;",
  "overflow-y: hidden;",
  "white-space: nowrap;",
  "text-align: center;",
]) {
  if (!formulaRule[0].includes(expected)) {
    console.error(`Expected volumetric formula CSS to include ${expected}`);
    process.exit(1);
  }
}
const formulaLineRule = css.match(/\.formula-group--volumetric \.formula-case \.book-formula-line \{[\s\S]*?\n\}/);
if (!formulaLineRule) {
  console.error("Expected volumetric formula line rule in theme/custom.css");
  process.exit(1);
}
for (const expected of [
  "width: 100%;",
  "min-width: 0;",
  "text-align: center;",
]) {
  if (!formulaLineRule[0].includes(expected)) {
    console.error(`Expected volumetric formula line CSS to include ${expected}`);
    process.exit(1);
  }
}
const formulaCopyRule = css.match(/\.formula-group--volumetric \.formula-case-copy \{[\s\S]*?\n\}/);
if (!formulaCopyRule) {
  console.error("Expected volumetric formula copy rule in theme/custom.css");
  process.exit(1);
}
for (const expected of [
  "justify-self: start;",
  "width: 100%;",
  "text-align: left;",
]) {
  if (!formulaCopyRule[0].includes(expected)) {
    console.error(`Expected volumetric formula copy CSS to include ${expected}`);
    process.exit(1);
  }
}
const formulaConnectorRule = css.match(/\.formula-case-connector \{[\s\S]*?\n\}/);
if (!formulaConnectorRule) {
  console.error("Expected formula connector rule in theme/custom.css");
  process.exit(1);
}
for (const expected of [
  "justify-self: start;",
  "text-align: left;",
]) {
  if (!formulaConnectorRule[0].includes(expected)) {
    console.error(`Expected formula connector CSS to include ${expected}`);
    process.exit(1);
  }
}
const mobileFormulaStart = css.indexOf("@media (max-width: 760px) {", css.indexOf(".formula-case-grid {"));
const mobileFormulaEnd = css.indexOf(".reader-article td .formula-card,", mobileFormulaStart);
if (mobileFormulaStart === -1 || mobileFormulaEnd === -1) {
  console.error("Expected narrow formula media query block in theme/custom.css");
  process.exit(1);
}
const mobileFormulaBlock = css.slice(mobileFormulaStart, mobileFormulaEnd);
for (const expected of [
  ".formula-group--volumetric .formula-case .book-formula {",
  "overflow-x: visible;",
  "overflow-y: visible;",
  "white-space: normal;",
  "line-height: 1.4;",
  ".formula-group--volumetric .formula-case .book-formula-line {",
  "width: 100%;",
  "min-width: 0;",
]) {
  if (!mobileFormulaBlock.includes(expected)) {
    console.error(`Expected narrow formula media CSS to include ${expected}`);
    process.exit(1);
  }
}
for (const expected of [
  ".formula-group--volumetric .formula-case .book-formula + .formula-case-connector {",
  "margin-top: 0.85rem;",
  ".formula-group--volumetric .formula-case-connector + .book-formula {",
  "margin-top: -1rem;",
]) {
  if (!css.includes(expected)) {
    console.error(`Expected volumetric connector spacing CSS to include ${expected}`);
    process.exit(1);
  }
}
NODE

node - <<'NODE'
const fs = require("fs");
const css = fs.readFileSync("theme/custom.css", "utf8");
const mobileReaderStart = css.lastIndexOf("@media (max-width: 760px) {");
const mobileReaderEnd = css.indexOf("@media (max-width: 1023px) {", mobileReaderStart);
if (mobileReaderStart === -1 || mobileReaderEnd === -1) {
  console.error("Expected narrow reader layout media query block in theme/custom.css");
  process.exit(1);
}
const mobileReaderBlock = css.slice(mobileReaderStart, mobileReaderEnd);
for (const expected of [
  ".reader-layout {",
  "padding: 1.5rem 0 2rem;",
  ".reader-main {",
  "padding: 24px 12px 40px;",
  "padding-inline-start: calc(12px + var(--reader-left-offset));",
  "padding-inline-end: 12px;",
]) {
  if (!mobileReaderBlock.includes(expected)) {
    console.error(`Expected narrow reader layout CSS to include ${expected}`);
    process.exit(1);
  }
}
NODE

# Reader projection contract
check_contains theme/custom.css '.book-sidebar-shell .chapter li a {'
check_contains theme/custom.css '.book-sidebar-shell .chapter li.part-title {'
check_exists scripts/build_static_reader_sidebar.mjs
check_contains package.json '"build:static-reader-sidebar": "node scripts/build_static_reader_sidebar.mjs"'
check_contains scripts/build_site.mjs 'scripts/build_static_reader_sidebar.mjs'
check_contains scripts/build_site.mjs 'scripts/build_reader_page_meta.mjs'
check_contains scripts/build_site.mjs 'scripts/localize_reader_shell.mjs'
check_contains scripts/build_site.mjs 'scripts/inject_book_seo.mjs'
check_contains scripts/build_site.mjs 'scripts/generate_book_sitemap.mjs'
check_contains scripts/build_site.mjs 'scripts/generate_site_robots.mjs'
check_contains scripts/build_site.mjs 'const editions = listSiteEditions();'
check_contains scripts/build_site.mjs 'editions.forEach(buildBookEdition);'
check_contains scripts/build_site.mjs 'editions.forEach(injectBookSeo);'
check_contains scripts/preview.sh 'npm run build:site >/dev/null'
check_contains scripts/preview.sh 'HOST="${HOST:-0.0.0.0}"'
check_contains scripts/preview.sh 'resolve_display_host() {'
check_contains scripts/preview.sh 'PREVIEW_DISPLAY_HOST'
check_contains scripts/preview.sh '["route", "-n", "get", "default"]'
check_contains scripts/preview.sh '["ipconfig", "getifaddr", default_interface]'
check_contains scripts/preview.sh 'DISPLAY_HOST="$(resolve_display_host "$HOST")"'
check_contains scripts/preview.sh 'RELOAD_TOKEN_FILE='
check_contains scripts/preview.sh 'scripts/preview_watch.mjs'
check_contains scripts/preview.sh 'French site:  http://$DISPLAY_HOST:$PORT/fr/'
check_contains scripts/preview.sh 'French book:  http://$DISPLAY_HOST:$PORT/fr/book/'
check_contains scripts/preview.sh '--display-host "$DISPLAY_HOST"'
check_contains scripts/preview.sh '--reload-token-file "$RELOAD_TOKEN_FILE"'
check_exists scripts/preview_watch.mjs
check_contains scripts/preview_watch.mjs 'const DEFAULT_WATCH_ROOTS = ["assets", "config", "editions", "scripts", "theme"];'
check_contains scripts/preview_watch.mjs 'function scheduleBuild(reason) {'
check_contains scripts/preview_watch.mjs 'async function runBuild() {'
check_contains scripts/preview_watch.mjs 'writeReloadToken(reloadTokenFile);'
check_contains scripts/preview_server.py 'parser.add_argument("--display-host")'
check_contains scripts/preview_server.py 'parser.add_argument("--reload-token-file")'
check_contains scripts/preview_server.py 'display_host = args.display_host or args.host'
check_contains scripts/preview_server.py 'if request_path == "/__preview/reload-token":'
check_contains scripts/preview_server.py 'data-preview-reload'
check_contains scripts/preview_server.py 'Serving preview on http://{display_host}:{args.port}/ from {args.directory}'
node -e 'const fs=require("fs");const hbs=fs.readFileSync("theme/index.hbs","utf8");for(const expected of ["<body class=\"book-layout-booting\">","sessionStorage.getItem(\"reader-sidebar-scroll-top\")","sessionStorage.setItem(\"reader-sidebar-scroll-top\"","document.body.classList.remove(\"book-layout-booting\");"]){if(!hbs.includes(expected)){console.error(`Expected theme/index.hbs to include ${expected}`);process.exit(1);}}for(const forbidden of ["window.bookPageVariants","applyInitialBookPageVariant","reader-sidebar-scroll-offset","customElements.whenDefined(\"mdbook-sidebar-scrollbox\")"]){if(hbs.includes(forbidden)){console.error(`Expected theme/index.hbs to stop including ${forbidden}`);process.exit(1);}}'
check_contains scripts/localize_reader_shell.mjs 'import { getBookPageBodyClasses } from "./shared/book-page-variants.mjs";'
check_contains scripts/localize_reader_shell.mjs 'function injectBodyClasses(html, pageKey) {'
check_contains scripts/localize_reader_shell.mjs 'html = injectBodyClasses(html, pageKey);'
check_contains scripts/shared/book-page-variants.mjs 'export function getBookPageBodyClasses(pageKey, locale) {'
check_contains scripts/shared/book-page-variants.mjs 'chapter-11-general-conclusion.html'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const chapterLink=block(".book-sidebar-shell .chapter li a {");for(const expected of ["font-size: 0.875rem;","line-height: 1.4286;"]){if(!chapterLink.includes(expected)){console.error(`Expected .book-sidebar-shell .chapter li a to include ${expected}`);process.exit(1);}}if(chapterLink.includes("font-size: 14px;")||chapterLink.includes("line-height: 20px;")||chapterLink.includes("font-size: 1.4rem;")||chapterLink.includes("line-height: 2rem;")){console.error("Expected .book-sidebar-shell .chapter li a to use repo-owned typography calibrated for the explicit /book root font contract");process.exit(1);}const partTitle=block(".book-sidebar-shell .chapter li.part-title {");if(!partTitle.includes("font-size: 0.75rem;")){console.error("Expected .book-sidebar-shell .chapter li.part-title to include font-size: 0.75rem;");process.exit(1);}if(partTitle.includes("font-size: 12px;")||partTitle.includes("font-size: 1.2rem;")){console.error("Expected .book-sidebar-shell .chapter li.part-title to stop using legacy sizing under the explicit /book root font contract");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const bookTitle=block(".book-sidebar-book-title {");if(!bookTitle.includes("color: var(--sidebar-fg);")){console.error("Expected .book-sidebar-book-title to align with the normal sidebar navigation text color.");process.exit(1);}const frontBackTitle=block(".reader-sidebar-section--front-matter .reader-sidebar-section-title,");if(!frontBackTitle.includes("color: var(--sidebar-fg);")){console.error("Expected Front Matter and Back Matter section titles to align with the normal sidebar navigation text color.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const sectionHeader=block(".reader-sidebar-section-header {");if(sectionHeader.includes("line-height: 25%;")){console.error("Expected sidebar section headers to stop relying on line-height: 25% for visual alignment; use explicit layout instead.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".reader-sidebar-section--front-matter .reader-sidebar-section-body,");if(start===-1){console.error("Expected Front Matter body selector to remain present in theme/custom.css");process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error("Expected closing brace for Front Matter body selector block");process.exit(1);}const frontMatterBody=css.slice(start,end+1);if(frontMatterBody.includes("padding-inline-start:")){console.error("Expected Front Matter body container position to remain unchanged; use row padding instead of container padding.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const activeRow=block(".reader-sidebar-row--active {");if(activeRow.includes("padding-inline-end:")){console.error("Expected active sidebar rows to preserve the same inline geometry as inactive rows; reserve the indicator gutter in the base row instead of shifting active items.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const visitedRow=block(".reader-sidebar-row:link,");for(const expected of ["color: var(--sidebar-fg);","-webkit-text-fill-color: var(--sidebar-fg);"]){if(!visitedRow.includes(expected)){console.error(`Expected reader sidebar normal link/visited contract to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const forbidden of ["function installSidebarProjection()","function readAndClearSidebarProjectionOffset()","sessionStorage.setItem(\"reader-sidebar-scroll-offset\"","sessionStorage.getItem(\"reader-sidebar-scroll-offset\""]){if(js.includes(forbidden)){console.error(`Expected theme/custom.js to stop including ${forbidden}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");const start=js.indexOf("function syncOutlineRailVisibility() {");const end=js.indexOf("\n\n  function syncOutlineActiveState()",start);if(start===-1||end===-1){console.error("Expected syncOutlineRailVisibility() to manage the empty right-rail contract.");process.exit(1);}const block=js.slice(start,end);for(const expected of ["document.querySelector(\"#mdbook-outline-scroll\")","document.querySelector(\".book-outline-body .on-this-page\")","document.querySelector(\".book-outline-figures\")","document.querySelector(\".book-outline-tables\")","document.querySelector(\".book-outline-formulas\")","document.body.classList.toggle(\"book-outline-empty\", !hasVisibleOutlineContent);","outline.hidden = !hasVisibleOutlineContent;"]){if(!block.includes(expected)){console.error(`Expected syncOutlineRailVisibility() to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const layout=block("body.book-outline-empty .reader-layout {");if(!layout.includes("grid-template-columns: minmax(0, 1fr);")){console.error("Expected empty outline pages to collapse the reader layout back to a single content column.");process.exit(1);}const rail=block("body.book-outline-empty .reader-outline {");if(!rail.includes("display: none;")){console.error("Expected empty outline pages to hide the desktop right rail entirely.");process.exit(1);}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function bindSidebarProjectionRowInteraction(","if (row.dataset.readerSidebarBound === \"true\") {","row.dataset.readerSidebarBound = \"true\";","hydrateSidebarProjectionRows(projection);"]){if(!js.includes(expected)){console.error(`Expected theme/custom.js to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function installSidebarDisplayStateSync()","function syncSidebarDisplayState()","if (!sidebarToggle.checked) {","if (sidebar.style.display === \"none\") {","sidebar.style.display = \"\";","sidebar.offsetHeight;","sidebar.setAttribute(\"aria-hidden\", \"false\");","requestAnimationFrame(syncSidebarDisplayState);","installSidebarDisplayStateSync();"]){if(!js.includes(expected)){console.error(`Expected theme/custom.js to include ${expected}`);process.exit(1);}}const displayIndex=js.indexOf("installSidebarDisplayStateSync();");const hydrateIndex=js.indexOf("hydrateSidebarProjectionRows(projection);");if(displayIndex===-1||hydrateIndex===-1||!(displayIndex<hydrateIndex)){console.error("Expected sidebar display-state sync to run before sidebar projection hydration.");process.exit(1);}'
check_contains theme/custom.js 'new ResizeObserver'
check_not_contains theme/custom.js '--sidebar-intro-height'
check_contains theme/custom.js 'reader-sidebar-scroll'
check_not_contains theme/custom.js '--sidebar-utilities-height'
if false; then
check_contains theme/custom.js 'reader-sidebar-projection'
check_contains theme/custom.js 'reader-sidebar-section'
check_contains theme/custom.js 'reader-sidebar-section-header'
check_contains theme/custom.js 'reader-sidebar-section-icon'
check_contains theme/custom.js 'reader-sidebar-section-body'
check_contains theme/custom.js 'reader-sidebar-row'
check_contains theme/custom.js 'reader-sidebar-row-index'
check_contains theme/custom.js 'reader-sidebar-row-title'
check_contains theme/custom.js 'reader-sidebar-row--with-icon'
check_contains theme/custom.js 'reader-sidebar-row-icon'
check_contains theme/custom.js 'reader-sidebar-row--active'
check_contains theme/custom.js 'reader-sidebar-section--active'
check_contains theme/custom.js 'function buildSidebarSectionIcon('
check_contains theme/custom.js '"front-matter"'
check_contains theme/custom.js 'M12 5.75v13.4'
check_not_contains theme/custom.js 'book-sidebar-utility-link--active'
check_contains theme/custom.js 'function getSidebarReferenceIcon('
check_contains theme/custom.js 'function buildSidebarReferenceIcon('
check_contains theme/custom.js 'function installSidebarProjection('
fi
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-projection'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-section'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-section-header'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-section-icon'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-section-body'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row-index'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row-title'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row--with-icon'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row-icon'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-row--active'
check_contains scripts/build_static_reader_sidebar.mjs 'reader-sidebar-section--active'
check_contains scripts/build_static_reader_sidebar.mjs '"front-matter"'
check_contains scripts/build_static_reader_sidebar.mjs 'M12 5.75v13.4'
check_contains scripts/build_static_reader_sidebar.mjs 'book-sidebar-shell--projected'
check_not_contains theme/custom.js 'book-sidebar-utility-link--active'
check_contains theme/custom.js 'function collectReferenceCards('
check_contains theme/custom.js 'function buildReferenceRailParts('
check_contains theme/custom.js 'function renderReferenceOutlineAnchor('
check_contains theme/custom.js 'function syncOutlineActiveState('
check_contains theme/custom.js 'function installOutlineScrollSpy('
check_contains theme/custom.js 'const outlineSource = document.querySelector("#mdbook-sidebar mdbook-sidebar-scrollbox .chapter-item > .on-this-page");'
check_contains theme/custom.js 'const outlineAnchors = Array.from(outlineSource.querySelectorAll("a.header-in-summary"));'
check_contains theme/custom.js 'outlineContainer.appendChild(buildOutlineList(outlineAnchors));'
check_not_contains theme/custom.js 'const outlineAnchors = Array.from(outlineBody.querySelectorAll(".on-this-page a.header-in-summary"));'
check_not_contains theme/custom.js 'const outlineAnchors = Array.from(document.querySelectorAll(".on-this-page a.header-in-summary"));'
check_contains scripts/shared/book-page-variants.mjs 'general-conclusion.html'
check_contains scripts/shared/book-page-variants.mjs 'glossary.html'
check_contains scripts/shared/book-page-variants.mjs 'bibliographical-references.html'
check_contains theme/custom.css '.reader-outline {'
check_contains theme/custom.css 'overflow-y: auto;'
check_contains theme/custom.css '#mdbook-page-wrapper {'
check_contains theme/custom.css 'overflow-y: hidden;'
check_contains theme/custom.css '#mdbook-menu-bar-hover-placeholder {'
check_contains theme/custom.css 'height: 0;'
check_contains theme/custom.css '.page {'
check_contains theme/custom.css 'display: flex;'
check_contains theme/custom.css 'flex-direction: column;'
check_contains theme/custom.css 'margin-block-start: 0;'
check_contains theme/custom.css 'padding: 0;'
check_contains theme/custom.css '.content {'
check_contains theme/custom.css 'overflow: hidden;'
check_contains theme/custom.css '.reader-main {'
check_contains theme/custom.css 'overflow-y: auto;'
check_contains theme/custom.css 'padding-inline-start: calc(24px + var(--reader-left-offset));'
check_contains theme/custom.css 'padding-inline-end: 24px;'
check_contains theme/custom.css 'transition: padding-inline-start 180ms ease;'
check_contains theme/custom.css 'body.book-layout-booting .reader-main,'
check_contains theme/custom.css 'body.book-layout-booting .book-progress {'
check_contains theme/custom.css 'transition: none !important;'
check_contains theme/custom.css '--brand-blue: #3163c2;'
check_contains theme/custom.css '--brand-blue-deep: #264d97;'
check_contains theme/custom.css '--brand-gold: #d9b24a;'
check_contains theme/custom.css '.reader-main-inner {'
check_contains theme/custom.css 'min-height: fit-content;'
check_contains theme/custom.css 'height: auto;'
check_contains theme/custom.css 'background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 251, 253, 0.96) 100%);'
check_contains theme/custom.css 'border-inline-start: 1px solid var(--book-rail-border);'
check_contains theme/custom.css '.book-progress {'
check_contains theme/custom.css 'margin-inline-start: var(--reader-left-offset);'
check_contains theme/custom.css 'width: calc(100% - var(--reader-left-offset));'
check_contains theme/custom.css 'transition: width 180ms ease, margin-inline-start 180ms ease;'
check_contains theme/custom.css '#mdbook-sidebar-toggle-anchor:checked ~ #mdbook-page-wrapper {'
check_contains theme/custom.css '--reader-left-offset: var(--sidebar-width);'
check_contains theme/custom.css 'margin-inline-start: 0;'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const mediaStart=css.indexOf("@media (max-width: 1080px) {");const mediaEnd=css.indexOf("@media (max-width: 760px) {", mediaStart);if(mediaStart===-1||mediaEnd===-1){console.error("Expected mobile sidebar media query block.");process.exit(1);}const mediaBlock=css.slice(mediaStart, mediaEnd);const match=mediaBlock.match(/#mdbook-sidebar-toggle-anchor:checked ~ #mdbook-page-wrapper \{([^}]*)\}/);if(!match){console.error("Expected mobile open-sidebar page wrapper rule.");process.exit(1);}for(const expected of ["transform: none;","margin-left: 0;","margin-inline-start: 0;"]){if(!match[1].includes(expected)){console.error(`Expected mobile open-sidebar page wrapper rule to include ${expected}`);process.exit(1);}}'
check_not_contains theme/custom.css '--toolbar-sidebar-column:'
check_not_contains theme/custom.css '--toolbar-actions-column:'
check_not_contains theme/custom.css 'width: min(100%, calc(100vw - var(--sidebar-width)));'
check_not_contains theme/custom.css 'margin-inline-start: var(--sidebar-width);'
check_contains theme/custom.css '.reader-article {'
check_contains theme/custom.css 'margin-inline: auto;'
check_contains theme/custom.css '.chapter-pagination {'
check_contains theme/custom.css 'margin-inline: auto;'
check_contains theme/custom.css 'max-width: var(--content-max-width);'
check_contains theme/custom.css '.book-outline-inner {'
check_contains theme/custom.css 'height: auto;'
check_contains theme/custom.css 'min-height: fit-content;'
check_contains theme/custom.css 'border: 0;'
check_contains theme/custom.css 'background: transparent;'
check_contains theme/custom.css 'box-shadow: none;'
check_contains theme/custom.css '.book-outline-label {'
check_contains theme/custom.css 'font-size: 11px;'
check_contains theme/custom.css '.book-outline-section {'
check_contains theme/custom.css '.book-outline-section-title {'
check_contains theme/custom.css '.book-outline-list {'
check_contains theme/custom.css '.book-outline-link--reference {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.reader-outline \.book-outline-link--reference-title \{[^}]*\}/);if(!block){console.error("Expected .reader-outline .book-outline-link--reference-title rule block");process.exit(1);}for(const expected of ["display: block;","white-space: normal;"]){if(!block[0].includes(expected)){console.error(`Expected outline reference title styling for: ${expected}`);process.exit(1);}}for(const forbidden of ["overflow: hidden;","display: -webkit-box;","-webkit-line-clamp: 2;"]){if(block[0].includes(forbidden)){console.error(`Did not expect outline reference title styling to include ${forbidden}`);process.exit(1);}}'
check_contains theme/custom.css '.on-this-page {'

# Reader hero and knowledge object contract
check_contains theme/custom.css '.reader-chapter-hero {'
check_contains theme/custom.css '.reader-chapter-hero .reader-chapter-eyebrow {'
check_contains theme/custom.css '.reader-chapter-rule {'
check_contains theme/custom.css '.reader-chapter-meta {'
check_contains theme/custom.css '.reader-chapter-meta--inline {'
check_contains theme/custom.css '.reader-chapter-meta-item--inline {'
check_contains theme/custom.css '.reader-chapter-dek {'
check_contains theme/custom.css '.reader-article--lead-figure-balanced .figure-card:first-of-type {'
check_contains theme/custom.css '.book-outline-active-marker {'
check_not_contains theme/custom.css '.reader-mobile-chapter-bar {'
check_not_contains theme/custom.css '.reader-mobile-chapter-toggle {'
check_contains theme/custom.css '.reader-mobile-outline-card {'
check_contains theme/custom.css '.reader-mobile-outline-card-header {'
check_contains theme/custom.css '.reader-mobile-outline-toggle {'
check_contains theme/custom.css '.reader-mobile-outline-card .on-this-page {'
check_contains theme/custom.css '.on-this-page .chapter-fold-toggle {'
check_contains theme/custom.css 'display: none;'
check_contains theme/custom.css '.on-this-page a,'
check_contains theme/custom.css '.on-this-page a:visited {'
check_contains theme/custom.css 'font-size: 13px;'
check_contains theme/custom.css 'color: var(--ink);'
check_contains theme/custom.css '.content h1 {'
check_contains theme/custom.css '.content main {'
check_contains theme/custom.css 'font-size: 16px;'
check_contains theme/custom.css 'line-height: 1.72;'
check_contains theme/custom.css '.content h1 {'
check_contains theme/custom.css 'font-size: 30px;'
check_contains theme/custom.css '@media (min-width: 768px) {'
check_contains theme/custom.css 'font-size: 36px;'
check_contains theme/custom.css '.content h2 {'
check_contains theme/custom.css 'font-size: 24px;'
check_contains theme/custom.css '.content h3 {'
check_contains theme/custom.css 'font-size: 20px;'
check_contains theme/custom.css '.reader-article p {'
check_contains theme/custom.css '--reader-article-body-measure: 68ch;'
check_contains theme/custom.css '--reader-article-body-width: 39rem;'
check_contains theme/custom.css '--reader-heading-measure: 34ch;'
check_contains theme/custom.css '--reader-chapter-title-measure: 26ch;'
check_contains theme/custom.css 'max-width: var(--reader-article-body-measure);'
check_contains theme/custom.css '--reader-article-column-max: min(100%, var(--reader-article-body-width));'
check_contains theme/custom.css 'grid-template-columns: minmax(0, 1fr) minmax(0, var(--reader-article-column-max)) minmax(0, 1fr);'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");for(const selector of [".reader-article p {",".reader-article ul {",".reader-article ol {"]){const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);for(const expected of ["max-width: var(--reader-article-body-measure);","margin-inline: auto;"]){if(!block.includes(expected)){console.error(`Expected ${selector} to include ${expected}`);process.exit(1);}}}const liSelector=".reader-article li {";const liStart=css.indexOf(liSelector);const liEnd=css.indexOf("}",liStart);if(liStart===-1||liEnd===-1){console.error(`Expected rule block for ${liSelector}`);process.exit(1);}const liBlock=css.slice(liStart,liEnd+1);if(!liBlock.includes("max-width: none;")){console.error("Expected list items to fill the shared list container instead of centering themselves.");process.exit(1);}if(liBlock.includes("margin-inline: auto;")){console.error("Expected list items to stop centering themselves independently.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const sharedHeadingBlocks=[...css.matchAll(/\.reader-article h2,\s*\.reader-article h3,\s*\.reader-article h4,\s*\.reader-article h5,\s*\.reader-article h6 \{[^}]*\}/g)].map((match)=>match[0]);const sharedHeadingBlock=sharedHeadingBlocks.find((block)=>block.includes("margin-inline: auto;"));if(!sharedHeadingBlock){console.error("Expected shared reader heading positioning rule block.");process.exit(1);}for(const expected of ["position: relative;","margin-inline: auto;"]){if(!sharedHeadingBlock.includes(expected)){console.error(`Expected shared reader heading positioning rule to include ${expected}`);process.exit(1);}}const h2Match=css.match(/\.reader-article h2 \{[^}]*\}/);if(!h2Match||!h2Match[0].includes("max-width: calc(var(--reader-article-body-measure) * var(--reader-h2-body-align-scale));")){console.error("Expected h2 headings to scale body measure by the h2 alignment ratio.");process.exit(1);}const h3Matches=[...css.matchAll(/\.reader-article h3,\s*\.reader-article h4,\s*\.reader-article h5,\s*\.reader-article h6 \{[^}]*\}/g)].map((match)=>match[0]);const h3MeasureBlock=h3Matches.find((block)=>block.includes("max-width: calc(var(--reader-article-body-measure) * var(--reader-h3-body-align-scale));"));if(!h3MeasureBlock){console.error("Expected h3-h6 headings to scale body measure by the subheading alignment ratio.");process.exit(1);}const anchorSelector=".reader-article a.header.reader-heading-link--indexed,";const anchorStart=css.indexOf(anchorSelector);const anchorEnd=css.indexOf("}",anchorStart);if(anchorStart===-1||anchorEnd===-1){console.error(`Expected rule block for ${anchorSelector}`);process.exit(1);}const anchorBlock=css.slice(anchorStart,anchorEnd+1);for(const expected of ["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.85rem;","align-items: start;","width: 100%;","max-width: 100%;"]){if(!anchorBlock.includes(expected)){console.error(`Expected ${anchorSelector} to include ${expected}`);process.exit(1);}}const indexSelector=".reader-article a.header.reader-heading-link--indexed .reader-heading-index {";const indexStart=css.indexOf(indexSelector);const indexEnd=css.indexOf("}",indexStart);if(indexStart===-1||indexEnd===-1){console.error(`Expected rule block for ${indexSelector}`);process.exit(1);}const indexBlock=css.slice(indexStart,indexEnd+1);for(const expected of ["position: relative;","text-align: start;"]){if(!indexBlock.includes(expected)){console.error(`Expected ${indexSelector} to include ${expected}`);process.exit(1);}}for(const removed of ["position: absolute;","right: calc(100% + 0.85rem);","text-align: right;"]){if(indexBlock.includes(removed)){console.error(`Expected ${indexSelector} to remove ${removed}`);process.exit(1);}}const selector=".reader-article a.header.reader-heading-link--indexed .reader-heading-title {";const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);for(const expected of ["display: block;","max-width: var(--reader-heading-measure);","width: 100%;","text-wrap: balance;"]){if(!block.includes(expected)){console.error(`Expected ${selector} to include ${expected}`);process.exit(1);}}const subheadingSelector=".reader-article > h3 > a.header.reader-heading-link--indexed .reader-heading-title,";const subheadingStart=css.indexOf(subheadingSelector);const subheadingEnd=css.indexOf("}",subheadingStart);if(subheadingStart===-1||subheadingEnd===-1){console.error("Expected h3-h6 heading title width override block.");process.exit(1);}const subheadingBlock=css.slice(subheadingStart,subheadingEnd+1);for(const expected of [".reader-article > h3 > a.header.reader-heading-link--indexed .reader-heading-title,", ".reader-article > h3 > a.header.reader-heading-link--indexed:visited .reader-heading-title,", ".reader-article > h4 > a.header.reader-heading-link--indexed .reader-heading-title,", ".reader-article > h4 > a.header.reader-heading-link--indexed:visited .reader-heading-title,", ".reader-article > h5 > a.header.reader-heading-link--indexed .reader-heading-title,", ".reader-article > h5 > a.header.reader-heading-link--indexed:visited .reader-heading-title,", ".reader-article > h6 > a.header.reader-heading-link--indexed .reader-heading-title,", ".reader-article > h6 > a.header.reader-heading-link--indexed:visited .reader-heading-title {", "width: var(--reader-article-body-width);", "max-width: var(--reader-article-body-width);", "justify-self: stretch;"]){if(!subheadingBlock.includes(expected)){console.error(`Expected h3-h6 heading title width override for ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const spanBlocks=[...css.matchAll(/\.reader-article > h3,[\s\S]*?\}/g)].map((match)=>match[0]);const spanBlock=spanBlocks.find((block)=>block.includes("grid-column: 2 / 4;"));if(!spanBlock){console.error("Expected h3-h6 outer grid-span rule block.");process.exit(1);}for(const expected of [".reader-article > h3,",".reader-article > h4,",".reader-article > h5,",".reader-article > h6 {","grid-column: 2 / 4;","width: auto;","max-width: none;","justify-self: start;"]){if(!spanBlock.includes(expected)){console.error(`Expected h3-h6 outer grid-span rule to include ${expected}`);process.exit(1);}}const wideAnchorBlocks=[...css.matchAll(/\.reader-article > h3 > a\.header\.reader-heading-link--indexed,[\s\S]*?\}/g)].map((match)=>match[0]);const wideAnchorBlock=wideAnchorBlocks.find((block)=>block.includes("grid-template-columns: auto minmax(0, var(--reader-article-body-width));"));if(!wideAnchorBlock){console.error("Expected h3-h6 widened anchor rule block.");process.exit(1);}for(const expected of [".reader-article > h3 > a.header.reader-heading-link--indexed,",".reader-article > h3 > a.header.reader-heading-link--indexed:visited,",".reader-article > h4 > a.header.reader-heading-link--indexed,",".reader-article > h4 > a.header.reader-heading-link--indexed:visited,",".reader-article > h5 > a.header.reader-heading-link--indexed,",".reader-article > h5 > a.header.reader-heading-link--indexed:visited,",".reader-article > h6 > a.header.reader-heading-link--indexed,",".reader-article > h6 > a.header.reader-heading-link--indexed:visited {","grid-template-columns: auto minmax(0, var(--reader-article-body-width));","width: max-content;","max-width: 100%;"]){if(!wideAnchorBlock.includes(expected)){console.error(`Expected h3-h6 widened anchor rule to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const sharedColumnBlock=css.match(/\.reader-article > h1,\s*\.reader-article > \.reference-index \{[^}]*\}/);if(!sharedColumnBlock){console.error("Expected non-hero article h1 and reference index containers to share the article content column.");process.exit(1);}for(const expected of ["grid-column: 2;","width: 100%;","max-width: none;","margin-inline: 0;"]){if(!sharedColumnBlock[0].includes(expected)){console.error(`Expected shared non-hero content-column rule to include ${expected}`);process.exit(1);}}const introBlock=css.match(/\.reference-index-intro \{[^}]*\}/);if(!introBlock){console.error("Expected reference index intro rule block.");process.exit(1);}for(const expected of ["max-width: none;","margin-inline: 0;"]){if(!introBlock[0].includes(expected)){console.error(`Expected reference index intro rule to include ${expected}`);process.exit(1);}}if(introBlock[0].includes("max-width: 60ch;")){console.error("Expected reference index intro to stop using a narrower centered measure.");process.exit(1);}'
check_contains theme/custom.css '.content table {'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function normalizeHeadingDisplayText(text)","function splitHeadingDisplayText(text)","function renderIndexedHeadingAnchor(anchor, text)","function renderOutlineHeadingAnchor(anchor, text)","anchor.dataset.readerHeadingDisplayText = normalizedText;","document.querySelectorAll(\".reader-article a.header\")","renderIndexedHeadingAnchor(anchor, anchor.textContent);","renderOutlineHeadingAnchor(","entry.marker.classList.toggle(\"book-outline-active-marker--visible\", isActive);"]){if(!js.includes(expected)){console.error(`Expected heading hyphen cleanup behavior for: ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const checks=[["\n.reader-chapter-hero {",["display: grid;","width: min(100%, var(--reader-article-body-measure));","margin-inline: auto;"]],[".reader-chapter-hero .reader-chapter-eyebrow {",["display: inline-flex;","justify-self: start;","padding: 0.45rem 0.85rem;","background: linear-gradient(180deg, rgba(255, 250, 240, 0.98) 0%, rgba(248, 238, 210, 0.94) 100%);","color: var(--brand-gold);","font-family: var(--reader-sans);","font-size: 12px;","letter-spacing: 0.12em;"]],[".reader-chapter-hero h1 {",["font-size: 48px;","line-height: 1.08;","max-width: var(--reader-chapter-title-measure);","text-wrap: balance;"]],[".reader-article h1:target::before,",["display: none;","content: none;"]],[".reader-article a.header.reader-heading-link--indexed,",["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.85rem;","align-items: start;","color: var(--ink);","text-decoration: none;"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-index {",["position: relative;","padding-bottom: 0.8rem;","color: var(--brand-blue);","text-align: start;","white-space: nowrap;"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-index::after {",["width: 100%;","height: 4px;","background: var(--brand-gold);"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-title {",["display: block;","min-width: 0;"]],[".reader-chapter-rule {",["width: 32px;","height: 3px;","justify-self: start;"]],[".reader-chapter-meta-item {",["font-size: 14px;"]],[".book-outline-label {",["color: var(--links);"]],[".book-outline-section-title {",["color: var(--links);"]],[".book-outline-link,",["color: var(--ink);"]],[".book-outline-link--active,",["color: var(--ink);","font-weight: 600;"]],[".reader-outline {",["min-width: 0;","overflow-x: clip;"]],[".book-outline-inner {",["gap: 2rem;","min-width: 0;"]],[".book-outline-section {",["gap: 1.25rem;","padding-top: 2rem;"]],[".reader-outline .book-outline-link:link,",["color: var(--ink);"]],[".reader-outline .book-outline-link--indexed,",["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.48rem;"]],[".reader-outline .book-outline-link--indexed .book-outline-heading-index {",["margin-right: 0;","white-space: nowrap;","color: var(--links);"]],[".reader-outline .book-outline-link--indexed .book-outline-heading-title {",["color: var(--ink);"]],[".on-this-page a.active,",["color: var(--ink);","font-weight: 600;"]],[".on-this-page {",["--book-outline-font-size: 13px;","--book-outline-line-height: 1.25;","--book-outline-marker-size: 0.4375rem;","--book-outline-marker-gap: 0.4rem;","min-width: 0;"]],[".on-this-page .chapter-link-wrapper {",["position: relative;","display: block;","width: 100%;","min-width: 0;","box-sizing: border-box;"]],[".on-this-page li.header-item {",["min-width: 0;"]],[".on-this-page .chapter-link-wrapper[data-heading-tag=\"h3\"] {",["padding-inline-start: 1rem;"]],[".on-this-page .chapter-link-wrapper[data-heading-tag=\"h4\"] {",["padding-inline-start: 2rem;"]],[".on-this-page a:focus-visible,",["color: var(--ink);"]],[".reader-mobile-outline-card {",["padding: 14px 16px;","border-radius: 14px;"]],[".reader-mobile-outline-card-header {",["display: flex;","justify-content: space-between;"]],[".reader-mobile-outline-toggle {",["font-size: 0.875rem;","font-weight: 600;"]],[".reader-mobile-outline-card .on-this-page > ol {",["display: grid;","grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr));","gap: 0.65rem 1rem;"]],[".reader-mobile-outline-card .on-this-page li.header-item {",["display: block;","min-width: 0;","max-width: 100%;"]],[".book-outline-active-marker {",["display: flex;","position: absolute;","inset-inline-start: calc(-1 * (var(--book-outline-marker-size) + var(--book-outline-marker-gap)));","top: calc((var(--book-outline-font-size) * var(--book-outline-line-height) - var(--book-outline-marker-size)) / 2);","height: var(--book-outline-marker-size);","opacity: 0;"]],[".book-outline-active-marker--visible {",["opacity: 1;"]],[".book-outline-link--indexed .book-outline-heading-index {",["margin-right: 0.24rem;"]]];for(const [selector,expected] of checks){const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);for(const value of expected){if(!block.includes(value)){console.error(`Expected ${selector} to include ${value}`);process.exit(1);}}if(selector === ".reader-chapter-hero .reader-chapter-eyebrow {" && block.includes("border-radius:")){console.error("Expected .reader-chapter-eyebrow to remove rounded corners");process.exit(1);}}for(const removed of [".reader-mobile-chapter-toggle {",".reader-mobile-chapter-kicker {",".reader-mobile-chapter-title {"]){if(css.includes(removed)){console.error(`Expected mobile chapter selector styles to be removed: ${removed}`);process.exit(1);}}const heroTitleBlocks=[...css.matchAll(/\.reader-chapter-hero h1 \{[^}]*\}/g)].map((match)=>match[0]);if(heroTitleBlocks.length===0){console.error("Expected chapter hero title rule blocks");process.exit(1);}for(const block of heroTitleBlocks){if(!block.includes("font-size: 48px;")){console.error("Expected every chapter hero title rule block to use font-size: 48px;");process.exit(1);}if(!block.includes("max-width: var(--reader-chapter-title-measure);")){console.error("Expected every chapter hero title rule block to use the shared chapter title measure.");process.exit(1);}if(block.includes("font-size: clamp(")){console.error("Expected chapter hero title size to use fixed 48px instead of clamp");process.exit(1);}}'
check_contains theme/custom.css '.reader-article table,'
check_contains theme/custom.css 'font-family: var(--reader-sans);'
check_contains theme/custom.css 'font-size: 14px;'
check_contains theme/custom.css 'body.book-page-cover .reader-layout {'
check_contains theme/custom.css 'body.book-page-cover .reader-outline {'
check_contains theme/custom.css 'body.book-page-cover .chapter-pagination {'
check_contains theme/custom.css 'body.book-page-aux-index {'
check_not_contains theme/custom.css 'body.book-page-aux-index .reader-layout {'
check_contains theme/custom.css 'body.book-page-aux-index .reader-article {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const wideRailStart=css.indexOf("@media (min-width: 1281px) {");const wideRailEnd=css.indexOf("}\n\n@media (max-width: 1280px) {",wideRailStart);if(wideRailStart===-1||wideRailEnd===-1){console.error("Expected wide-screen outline rail preservation media block.");process.exit(1);}const block=css.slice(wideRailStart,wideRailEnd+1);for(const expected of ["body.book-page-cover .reader-layout,","body.book-page-aux-index .reader-layout,","body.book-page-front-matter-outline-rail .reader-layout {","grid-template-columns: minmax(0, 1fr) var(--outline-width);","body.book-page-cover .reader-outline,","body.book-page-aux-index .reader-outline,","body.book-page-front-matter-outline-rail .reader-outline,","body.book-page-cover .reader-outline[hidden],","body.book-page-front-matter-outline-rail .reader-outline[hidden] {","display: block !important;"]){if(!block.includes(expected)){console.error(`Expected wide-screen outline rail preservation block to include ${expected}`);process.exit(1);}}'
check_not_contains theme/custom.css 'max-width: 880px;'
check_contains theme/custom.css '.book-cover {'
check_contains theme/custom.css '.book-cover-frame {'
check_contains theme/custom.css '.book-cover-title {'
check_contains theme/custom.css 'padding-bottom: clamp(1.5rem, 3vw, 2.75rem);'
check_contains theme/custom.css '.book-cover-figure img {'
check_contains theme/custom.css 'aspect-ratio: 16 / 9;'
check_contains theme/custom.css '.book-cover-footer {'
check_contains theme/custom.css 'min-height: min(940px, calc(100vh - 7rem));'
check_contains theme/custom.css '@media (max-width: 760px) {'
check_contains theme/custom.css 'padding: 22px 20px 20px;'
check_contains theme/custom.css 'inset: 12px;'
check_contains theme/custom.css '.reference-index {'
check_contains theme/custom.css 'font-size: 17px;'
check_contains theme/custom.css 'padding: 14px 16px 18px;'
check_contains theme/custom.css 'font-size: 18px;'
check_contains theme/custom.css 'list-style: none;'
check_contains theme/custom.css 'padding-left: 0;'
check_contains theme/custom.css '.reference-index .reference-index-link:link,'
check_contains theme/custom.css '.reference-index .reference-index-link:visited {'
check_contains theme/custom.css 'color: var(--primary);'
check_contains theme/custom.css 'text-decoration-color: rgba(43, 91, 166, 0.18);'
check_contains theme/custom.css '.reference-index-link {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const listBlock=css.match(/\.reference-index-list \{[^}]*\}/);if(!listBlock){console.error("Expected .reference-index-list rule block");process.exit(1);}for(const expected of ["display: grid;","grid-template-columns: minmax(0, 1fr);","width: 100%;","max-width: none;"]){if(!listBlock[0].includes(expected)){console.error(`Expected .reference-index-list to include ${expected}`);process.exit(1);}}const liBlock=css.match(/\.reference-index-list > li \{[^}]*\}/);if(!liBlock||!liBlock[0].includes("min-width: 0;")){console.error("Expected .reference-index-list > li to preserve min-width: 0; so TOC rows cannot shrink-wrap their content.");process.exit(1);}const linkBlock=css.match(/\.reference-index-link \{[^}]*\}/);if(!linkBlock){console.error("Expected .reference-index-link rule block");process.exit(1);}for(const expected of ["display: block;","width: 100%;","text-decoration: none;"]){if(!linkBlock[0].includes(expected)){console.error(`Expected .reference-index-link to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");for(const forbidden of [".reference-index-heading-link {",".reference-index-heading-title {",".reference-index-heading-page {",".reference-index-list--toc {",".reference-index-toc-link {",".reference-index-toc-label,",".reference-index-toc-label {",".reference-index-toc-title {",".reference-index-toc-page {"]){if(css.includes(forbidden)){console.error(`Expected TOC-specific selector to be removed: ${forbidden}`);process.exit(1);}}'
check_contains theme/custom.css '.reference-glossary-list {'
check_not_contains theme/custom.css '.reference-index-list li::marker {'
check_contains theme/custom.css '.reference-glossary-item {'
check_contains theme/custom.css '.reader-article .book-formula {'
check_contains theme/custom.css '.book-formula-line {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".book-formula-line {");const end=css.indexOf("}\n\n.book-formula-bridge",start);if(start===-1||end===-1){console.error("Expected .book-formula-line rule block");process.exit(1);}const block=css.slice(start,end+1);if(!block.includes("font-style: normal;")){console.error("Expected .book-formula-line to use normal font style");process.exit(1);}if(block.includes("font-style: italic;")){console.error("Did not expect .book-formula-line to keep italic font style");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const bridgeStart=css.indexOf(".book-formula-bridge {");const bridgeEnd=css.indexOf("}\n\n.formula-anchor-target",bridgeStart);if(bridgeStart===-1||bridgeEnd===-1){console.error("Expected .book-formula-bridge rule block");process.exit(1);}const bridgeBlock=css.slice(bridgeStart,bridgeEnd+1);for(const expected of ["text-align: left;","color: rgba(15, 23, 42, 0.86);","font-size: 0.92rem;","font-weight: 800;","letter-spacing: 0.16em;"]){if(!bridgeBlock.includes(expected)){console.error(`Expected formula bridge styling for: ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const singleStart=css.indexOf(".reader-article .book-formula {");const singleEnd=css.indexOf("}\n\n.reader-article .book-formula:not(.api-density-formula)",singleStart);const outerStart=css.indexOf(".reader-article .book-formula:not(.api-density-formula) {");const outerEnd=css.indexOf("}\n\n.reader-article .api-density-formula",outerStart);const prospectStart=css.indexOf(".formula-group--prospect > .book-formula,");const prospectEnd=css.indexOf("}\n\n.formula-group--prospect > .book-formula .book-formula-line,",prospectStart);const splitStart=css.indexOf(".formula-group--split > .formula-split-entry > .book-formula {");const splitEnd=css.indexOf("}\n\n.formula-group--split > .formula-split-entry:first-child > .book-formula",splitStart);const panelStart=css.indexOf(".formula-panel .book-formula--panel-row {");const panelEnd=css.indexOf("}\n\n.formula-panel .book-formula--panel-row::before",panelStart);if(singleStart===-1||singleEnd===-1||outerStart===-1||outerEnd===-1||prospectStart===-1||prospectEnd===-1||splitStart===-1||splitEnd===-1||panelStart===-1||panelEnd===-1){console.error("Expected formula rule blocks");process.exit(1);}const singleBlock=css.slice(singleStart,singleEnd+1);const outerBlock=css.slice(outerStart,outerEnd+1);const prospectBlock=css.slice(prospectStart,prospectEnd+1);const splitBlock=css.slice(splitStart,splitEnd+1);const panelBlock=css.slice(panelStart,panelEnd+1);for(const [name,block,expected] of [["single",singleBlock,["font-size: 16px;","line-height: 1.2;"]],["prospect",prospectBlock,["font-size: clamp(20px, 1.55vw, 25px);","line-height: 1.2;"]],["split",splitBlock,["font-size: 16px;","line-height: 1.28;"]],["panel",panelBlock,["font-size: 16px;","line-height: 1.28;"]]]){for(const value of expected){if(!block.includes(value)){console.error(`Expected ${name} formulas to include ${value}`);process.exit(1);}}}for(const expected of ["margin: 24px 0 22px;"]){if(!singleBlock.includes(expected)){console.error(`Expected standalone formula block to include ${expected}`);process.exit(1);}}for(const expected of ["justify-items: start;","text-align: left;"]){if(!outerBlock.includes(expected)){console.error(`Expected standalone non-table formula alignment for ${expected}`);process.exit(1);}}for(const forbidden of ["margin: 24px auto 22px;","justify-items: center;","text-align: center;"]){if(singleBlock.includes(forbidden)||outerBlock.includes(forbidden)){console.error(`Did not expect standalone non-table formulas to include ${forbidden}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".reader-article > .book-formula,");const end=css.indexOf("}\n\n.formula-group {",start);if(start===-1||end===-1){console.error("Expected top-level article formula column rule block");process.exit(1);}const block=css.slice(start,end+1);for(const selector of [".reader-article > .book-formula,",".reader-article > .formula-anchor-target,",".reader-article > .formula-group,",".reader-article > .formula-panel,",".reader-article > .formula-derivation,",".reader-article > .formula-where {"]){if(!block.includes(selector)){console.error(`Expected top-level article formula selector for ${selector}`);process.exit(1);}}for(const expected of ["grid-column: 2;","width: 100%;","max-width: none;","margin-inline: 0;"]){if(!block.includes(expected)){console.error(`Expected top-level article formulas to include ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.formula-derivation {'
check_contains theme/custom.css '.formula-panel {'
check_contains theme/custom.css '.formula-case-grid {'
check_contains theme/custom.css '.formula-case-title {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const panelStart=css.indexOf(".formula-panel {");const panelEnd=css.indexOf("}\n\n.formula-panel .book-formula--panel-row",panelStart);if(panelStart===-1||panelEnd===-1){console.error("Expected .formula-panel rule block");process.exit(1);}const panelBlock=css.slice(panelStart,panelEnd+1);for(const expected of ["padding: 0;","gap: 0.85rem;","border: 0;","background: transparent;","box-shadow: none;"]){if(!panelBlock.includes(expected)){console.error(`Expected .formula-panel to include: ${expected}`);process.exit(1);}}const rowStart=css.indexOf(".formula-panel .book-formula--panel-row {");const rowEnd=css.indexOf("}\n\n.formula-panel .book-formula--panel-row::before",rowStart);if(rowStart===-1||rowEnd===-1){console.error("Expected .formula-panel .book-formula--panel-row rule block");process.exit(1);}const rowBlock=css.slice(rowStart,rowEnd+1);for(const expected of ["font-size: 16px;","font-weight: 520;","line-height: 1.28;"]){if(!rowBlock.includes(expected)){console.error(`Expected panel row formula styling for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.reader-article .api-density-formula {'
check_contains theme/custom.css '.api-density-fraction {'
check_contains theme/custom.css 'border-left: 3px solid rgba(43, 91, 166, 0.72);'
check_contains theme/custom.css 'box-shadow: 0 10px 24px rgba(15, 23, 42, 0.075);'
check_contains theme/custom.css 'font-family: var(--reader-serif);'
check_contains theme/custom.css 'padding: 13px 22px 12px;'
check_contains theme/custom.css 'font-size: 16px;'
check_contains theme/custom.css 'min-width: 5.8em;'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.reader-article \.api-density-formula \{[^}]*\}/);if(!block||!/font-weight:\s*500;/.test(block[0])){console.error("Expected .api-density-formula to use font-weight: 500");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".toolbar-sidebar {");const end=css.indexOf("}\n\n.toolbar-main {",start);if(start===-1||end===-1){console.error("Expected .toolbar-sidebar rule block");process.exit(1);}const block=css.slice(start,end+1);if(block.includes("border-inline-end:")){console.error("Did not expect .toolbar-sidebar to keep a right divider");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.api-density-numerator \{[^}]*\}/);if(!block||!/border-bottom:\s*0\.055em solid currentColor;/.test(block[0])){console.error("Expected .api-density-numerator to use border-bottom: 0.055em solid currentColor");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".reader-article td .formula-card,");const end=css.indexOf("}\n\n.reader-article td .formula-card > .book-formula,",start);if(start===-1||end===-1){console.error("Expected table formula card rule block");process.exit(1);}const block=css.slice(start,end+1);for(const expected of ["width: 100%;","margin: 0;","padding: 0.5rem 0.65rem;","background: var(--reader-table-card-bg);","box-shadow: none;","border-radius: 0.8rem;"]){if(!block.includes(expected)){console.error(`Expected table formula card styling for: ${expected}`);process.exit(1);}}if(block.includes("padding: var(--reader-table-card-padding);")){console.error("Expected table formula cards to stop using the roomy standalone card padding.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.reader-article td \.formula-anchor-target \+ \.formula-anchor-target,\s*\.reader-article th \.formula-anchor-target \+ \.formula-anchor-target \{[^}]*\}/);if(!block||!/margin-top:\s*0\.55rem;/.test(block[0])){console.error("Expected stacked table formulas to use compact vertical spacing");process.exit(1);}'
check_contains theme/custom.css '.figure-card {'
check_contains theme/custom.css 'box-sizing: border-box;'
check_contains theme/custom.css 'max-width: 100%;'
check_contains theme/custom.css '--reader-figure-border: 1px solid rgba(11, 31, 51, 0.1);'
check_contains theme/custom.css '--reader-figure-shell-shadow: 0 16px 32px rgba(15, 23, 42, 0.04);'
check_contains theme/custom.css '--reader-figure-caption-inset: 1rem;'
check_contains theme/custom.css '--figure-card-padding-block: 20px;'
check_contains theme/custom.css '--figure-card-padding-inline: 24px;'
check_contains theme/custom.css '--figure-card-bg: var(--sidebar-bg);'
check_contains theme/custom.css '--figure-media-padding: 0;'
check_contains theme/custom.css '--figure-media-radius: 12px;'
check_contains theme/custom.css '--figure-divider-gap: 0.95rem;'
check_contains theme/custom.css '--figure-caption-gap: 0.9rem;'
check_not_contains theme/custom.css 'padding-bottom: calc(var(--figure-card-padding-block) + 0.15rem);'
check_contains theme/custom.css 'border: var(--reader-figure-border);'
check_contains theme/custom.css 'box-shadow: var(--reader-figure-shell-shadow);'
check_contains theme/custom.css '.figure-media {'
check_contains theme/custom.css '.content p.figure-media,'
check_contains theme/custom.css 'width: 100%;'
check_contains theme/custom.css 'padding: var(--figure-media-padding) 0;'
check_contains theme/custom.css 'border-block: var(--figure-media-border);'
check_contains theme/custom.css 'border-inline: 0;'
check_contains theme/custom.css 'background: var(--figure-media-bg);'
check_contains theme/custom.css 'margin: 0;'
check_contains theme/custom.css '.figure-media-grid {'
check_contains theme/custom.css 'grid-template-columns: repeat(2, minmax(0, 1fr));'
check_contains theme/custom.css '.figure-card--panel-pair .figure-media-item img {'
check_not_contains theme/custom.css 'height: clamp(24rem, 42vw, 46rem);'
check_contains theme/custom.css 'object-fit: contain;'
check_contains theme/custom.css 'border: 0;'
check_not_contains theme/custom.css '.figure-card--flush-media {'
check_not_contains theme/custom.css '.figure-card--flush-media .figure-media-grid {'
check_not_contains theme/custom.css '.figure-card--inset-media {'
check_not_contains theme/custom.css 'max-width: calc(var(--figure-media-max-width) - 0.25rem);'
check_contains theme/custom.css '.figure-media-item {'
check_contains theme/custom.css '.figure-card-header {'
check_contains theme/custom.css '.figure-card-label {'
check_contains theme/custom.css '.figure-card-footer {'
check_contains theme/custom.css 'box-sizing: border-box;'
check_contains theme/custom.css 'margin-bottom: var(--figure-divider-gap);'
check_contains theme/custom.css 'display: grid;'
check_contains theme/custom.css 'grid-auto-flow: column;'
check_contains theme/custom.css 'justify-content: start;'
check_contains theme/custom.css '.figure-card-label::before {'
check_contains theme/custom.css 'display: block;'
check_contains theme/custom.css 'width: 24px;'
check_contains theme/custom.css 'height: 24px;'
check_contains theme/custom.css 'background-color: currentColor;'
check_contains theme/custom.css '-webkit-mask:'
check_contains theme/custom.css 'mask:'
check_contains theme/custom.css 'data:image/svg+xml'
check_not_contains theme/custom.css 'box-shadow: inset 4px 0 0 rgba(49, 99, 194, 0.15);'
check_contains theme/custom.css '.figure-card-title {'
check_contains theme/custom.css 'display: block;'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.figure-card-footer \{[^}]*\}/);if(!block){console.error("Expected .figure-card-footer rule block");process.exit(1);}for(const expected of ["width: calc(100% + (2 * var(--figure-card-padding-inline)));","margin-inline: calc(var(--figure-card-padding-inline) * -1);","padding: var(--figure-caption-gap) calc(var(--reader-figure-caption-inset) + var(--figure-card-padding-inline)) 0;","border-top: 0;","text-align: center;"]){if(!block[0].includes(expected)){console.error(`Expected figure footer block styling for: ${expected}`);process.exit(1);}}if(css.includes(".figure-card-footer::before")||css.includes("--figure-divider-extra-inset:")){console.error("Did not expect figure footer divider rule or inset token after removing the footer separator.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.figure-card-title \{[^}]*\}/);if(!block){console.error("Expected .figure-card-title rule block");process.exit(1);}for(const expected of ["font-size: 14px;","line-height: 1.55;","text-align: center;"]){if(!block[0].includes(expected)){console.error(`Expected figure title styling for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.figure-card img {'
check_contains theme/custom.css '.figure-anchor-target:target img {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const tableAnchor=css.indexOf(".table-anchor-target {");if(tableAnchor===-1){console.error("Expected .table-anchor-target rule after the mobile figure media query block.");process.exit(1);}const start=css.lastIndexOf("@media (max-width: 760px) {", tableAnchor);if(start===-1){console.error("Expected mobile figure media query block.");process.exit(1);}const block=css.slice(start, tableAnchor);if(block.includes("padding: 0.75rem 0;")){console.error("Expected mobile figure media to stop adding vertical padding overrides.");process.exit(1);}'
node -e "const fs=require('fs');const js=fs.readFileSync('theme/custom.js','utf8');if(!js.includes('captionLabel.textContent = \"Figure \" + match.number;')){console.error('Expected figure labels to render without a trailing colon.');process.exit(1);}if(js.includes('captionLabel.textContent = \"Figure \" + match.number + \":\";')){console.error('Expected figure labels to stop rendering a trailing colon.');process.exit(1);}"
check_contains theme/custom.css '.table-anchor-target {'
check_contains theme/custom.css '.table-card {'
check_contains theme/custom.css '.table-anchor-shell {'
check_contains theme/custom.css '.table-scroll {'
check_contains theme/custom.css '.table-anchor-target:target .table-card {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const cardBlock=css.match(/\.table-card \{[^}]*\}/);if(!cardBlock){console.error("Expected .table-card rule block");process.exit(1);}for(const expected of ["display: grid;","gap: 0;","padding: var(--reader-table-card-padding);","border: var(--reader-table-card-border);","background: var(--reader-table-card-bg);","box-shadow: var(--reader-table-card-shadow);"]){if(!cardBlock[0].includes(expected)){console.error(`Expected table card styling for: ${expected}`);process.exit(1);}}if(cardBlock[0].includes("linear-gradient(")){console.error("Expected table card background to stop using gradients.");process.exit(1);}const targetCardBlock=css.match(/\.table-anchor-target:target \.table-card \{[^}]*\}/);if(!targetCardBlock){console.error("Expected .table-anchor-target:target .table-card rule block");process.exit(1);}if(!targetCardBlock[0].includes("border-color: rgba(43, 91, 166, 0.22);")){console.error("Expected anchored table card styling to keep the border-color highlight.");process.exit(1);}if(targetCardBlock[0].includes("background:")){console.error("Expected anchored table card highlight to stop overriding the card background.");process.exit(1);}if(targetCardBlock[0].includes("box-shadow:")){console.error("Expected anchored table card highlight to stop adding a target-state shadow.");process.exit(1);}const mobileStart=css.indexOf("@media (max-width: 760px) {");if(mobileStart===-1){console.error("Expected mobile table media query block.");process.exit(1);}const mobileEnd=css.indexOf(".content {", mobileStart);const mobileBlock=css.slice(mobileStart, mobileEnd);if(mobileBlock.includes(".table-card {") && !mobileBlock.includes("padding: var(--reader-table-card-padding-mobile);")){console.error("Expected mobile table-card padding to use the tighter mobile token.");process.exit(1);}const shellBlock=css.match(/\.table-anchor-shell \{[^}]*\}/);if(!shellBlock){console.error("Expected .table-anchor-shell rule block");process.exit(1);}for(const expected of ["border: 0;","overflow: hidden;"]){if(!shellBlock[0].includes(expected)){console.error(`Expected table shell styling for: ${expected}`);process.exit(1);}}if(shellBlock[0].includes("border: 1px solid rgba(148, 163, 184, 0.22);")){console.error("Expected table shell border to move to the outer table card.");process.exit(1);}const scrollBlock=css.match(/\.table-scroll \{[^}]*\}/);if(!scrollBlock){console.error("Expected .table-scroll rule block");process.exit(1);}for(const expected of ["overflow-x: auto;","padding: 0;"]){if(!scrollBlock[0].includes(expected)){console.error(`Expected table scroll styling for: ${expected}`);process.exit(1);}}const notesGroupBlock=css.match(/\.table-notes-group \{[^}]*\}/);if(!notesGroupBlock){console.error("Expected .table-notes-group rule block");process.exit(1);}if(!notesGroupBlock[0].includes("margin-top: 0.6rem;")){console.error("Expected table notes group to preserve spacing after removing caption bottom gap.");process.exit(1);}const notesBlock=css.match(/\.content \.table-notes \{[^}]*\}/);if(!notesBlock){console.error("Expected .content .table-notes rule block");process.exit(1);}if(!notesBlock[0].includes("margin-bottom: 0;")){console.error("Expected table notes to explicitly remove bottom margin.");process.exit(1);}const anchorBlock=css.match(/\.table-anchor-table \{[^}]*\}/);if(!anchorBlock){console.error("Expected .table-anchor-table rule block");process.exit(1);}for(const expected of ["box-sizing: border-box;","width: 100%;","min-width: 100%;","margin: 0;"]){if(!anchorBlock[0].includes(expected)){console.error(`Expected table anchor block styling for: ${expected}`);process.exit(1);}}const table8Block=css.match(/#table-8 \.table-anchor-table \{[^}]*\}/);if(!table8Block||!table8Block[0].includes("min-width: 40rem;")){console.error("Expected Table 8 to pin a stable minimum width for mobile scrolling.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const cardBlock=css.match(/\.table-card \{[^}]*\}/);if(!cardBlock){console.error("Expected .table-card rule block");process.exit(1);}for(const expected of ["display: grid;","gap: 0;","padding: var(--reader-table-card-padding);","border: var(--reader-table-card-border);","background: var(--reader-table-card-bg);","box-shadow: var(--reader-table-card-shadow);"]){if(!cardBlock[0].includes(expected)){console.error(`Expected table card styling for: ${expected}`);process.exit(1);}}if(cardBlock[0].includes("linear-gradient(")){console.error("Expected table card background to stop using gradients.");process.exit(1);}const targetCardBlock=css.match(/\.table-anchor-target:target \.table-card \{[^}]*\}/);if(!targetCardBlock){console.error("Expected .table-anchor-target:target .table-card rule block");process.exit(1);}if(!targetCardBlock[0].includes("border-color: rgba(43, 91, 166, 0.22);")){console.error("Expected anchored table card styling to keep the border-color highlight.");process.exit(1);}if(targetCardBlock[0].includes("background:")){console.error("Expected anchored table card highlight to stop overriding the card background.");process.exit(1);}if(targetCardBlock[0].includes("box-shadow:")){console.error("Expected anchored table card highlight to stop adding a target-state shadow.");process.exit(1);}const mobileStart=css.indexOf("@media (max-width: 760px) {");if(mobileStart===-1){console.error("Expected mobile table media query block.");process.exit(1);}const mobileEnd=css.indexOf(".content {", mobileStart);const mobileBlock=css.slice(mobileStart, mobileEnd);if(mobileBlock.includes(".table-card {") && !mobileBlock.includes("padding: var(--reader-table-card-padding-mobile);")){console.error("Expected mobile table-card padding to use the tighter mobile token.");process.exit(1);}const shellBlock=css.match(/\.table-anchor-shell \{[^}]*\}/);if(!shellBlock){console.error("Expected .table-anchor-shell rule block");process.exit(1);}for(const expected of ["border: 0;","overflow: hidden;"]){if(!shellBlock[0].includes(expected)){console.error(`Expected table shell styling for: ${expected}`);process.exit(1);}}if(shellBlock[0].includes("border: 1px solid rgba(148, 163, 184, 0.22);")){console.error("Expected table shell border to move to the outer table card.");process.exit(1);}const scrollBlock=css.match(/\.table-scroll \{[^}]*\}/);if(!scrollBlock){console.error("Expected .table-scroll rule block");process.exit(1);}for(const expected of ["overflow-x: auto;","padding: 0;"]){if(!scrollBlock[0].includes(expected)){console.error(`Expected table scroll styling for: ${expected}`);process.exit(1);}}const notesGroupBlock=css.match(/\.table-notes-group \{[^}]*\}/);if(!notesGroupBlock){console.error("Expected .table-notes-group rule block");process.exit(1);}if(!notesGroupBlock[0].includes("margin-top: 0.6rem;")){console.error("Expected table notes group to preserve spacing after removing caption bottom gap.");process.exit(1);}const notesBlock=css.match(/\.content \.table-notes \{[^}]*\}/);if(!notesBlock){console.error("Expected .content .table-notes rule block");process.exit(1);}if(!notesBlock[0].includes("margin-bottom: 0;")){console.error("Expected table notes to explicitly remove bottom margin.");process.exit(1);}const anchorBlock=css.match(/\.table-anchor-table \{[^}]*\}/);if(!anchorBlock){console.error("Expected .table-anchor-table rule block");process.exit(1);}for(const expected of ["box-sizing: border-box;","width: 100%;","min-width: 100%;","margin: 0;"]){if(!anchorBlock[0].includes(expected)){console.error(`Expected table anchor block styling for: ${expected}`);process.exit(1);}}const table8Block=css.match(/#table-8 \.table-anchor-table \{[^}]*\}/);if(!table8Block||!table8Block[0].includes("min-width: 40rem;")){console.error("Expected Table 8 to pin a stable minimum width for mobile scrolling.");process.exit(1);}const table6FormulaBlock=css.match(/#table-6 \.table-6-rules-cell > \.book-formula \{[^}]*\}/);if(!table6FormulaBlock){console.error("Expected Table 6 formula sizing rule block.");process.exit(1);}for(const expected of ["margin: 0.25rem 0 0.35rem;","font-size: inherit;","line-height: 1.3;","box-shadow: none;","border-top-left-radius: 0;","border-bottom-left-radius: 0;"]){if(!table6FormulaBlock[0].includes(expected)){console.error(`Expected Table 6 formula styling for: ${expected}`);process.exit(1);}}const table6TextGapBlock=css.match(/#table-6 \.table-6-rules-cell > p \+ \.book-formula \{[^}]*\}/);if(!table6TextGapBlock||!table6TextGapBlock[0].includes("margin-top: 0.15rem;")){console.error("Expected Table 6 text-to-formula spacing override.");process.exit(1);}const table6FormulaGapBlock=css.match(/#table-6 \.table-6-rules-cell > \.book-formula \+ \.book-formula \{[^}]*\}/);if(!table6FormulaGapBlock||!table6FormulaGapBlock[0].includes("margin-top: 0.3rem;")){console.error("Expected Table 6 stacked formula spacing override.");process.exit(1);}const table6LastFormulaBlock=css.match(/#table-6 \.table-6-rules-cell > \.book-formula:last-child \{[^}]*\}/);if(!table6LastFormulaBlock||!table6LastFormulaBlock[0].includes("margin-bottom: 0;")){console.error("Expected Table 6 last formula bottom spacing override.");process.exit(1);}'
check_contains theme/custom.css '.content .table-caption {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.content \.table-caption \{[^}]*\}/);if(!block){console.error("Expected .content .table-caption rule block");process.exit(1);}for(const expected of ["max-width: none;","display: grid;","grid-template-columns: var(--reader-table-caption-icon-size) minmax(0, 1fr);","column-gap: 0.55rem;","row-gap: 8px;","margin-bottom: 24px;"]){if(!block[0].includes(expected)){console.error(`Expected table caption block styling for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.table-caption-icon {'
check_contains theme/custom.css '.table-caption-label {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.table-caption-label \{[^}]*\}/);if(!block){console.error("Expected .table-caption-label rule block");process.exit(1);}for(const expected of ["grid-column: 2;","display: block;","color: var(--primary-deep);"]){if(!block[0].includes(expected)){console.error(`Expected table caption label styling for: ${expected}`);process.exit(1);}}const iconBlock=css.match(/\.table-caption-icon \{[^}]*\}/);if(!iconBlock){console.error("Expected .table-caption-icon rule block");process.exit(1);}for(const expected of ["grid-row: 1 / span 2;","display: block;","width: var(--reader-table-caption-icon-size);","height: var(--reader-table-caption-icon-size);","-webkit-mask:","mask:","data:image/svg+xml"]){if(!iconBlock[0].includes(expected)){console.error(`Expected table caption icon styling for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.table-caption-text {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.table-caption-text \{[^}]*\}/);if(!block){console.error("Expected .table-caption-text rule block");process.exit(1);}for(const expected of ["grid-column: 2;","display: block;","color: var(--ink);","font-size: 14px;","font-style: normal;"]){if(!block[0].includes(expected)){console.error(`Expected table caption text styling for: ${expected}`);process.exit(1);}}if(block[0].includes("padding-inline-start:")){console.error("Expected table caption text to stop using hard-coded inline padding for alignment.");process.exit(1);}if(block[0].includes("font-size: 16px;")){console.error("Expected table caption text to stop using 16px.");process.exit(1);}if(block[0].includes("font-style: italic;")){console.error("Expected table caption text to stop using italic style.");process.exit(1);}if(block[0].includes("line-height: 0;")){console.error("Expected table caption text to stop forcing line-height: 0.");process.exit(1);}'
check_contains theme/custom.css '.content .table-notes {'
check_contains theme/custom.css 'font-family: var(--reader-serif);'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");if(!css.includes(".content td {\n  background: var(--paper);\n}")){console.error("Expected table body cells to use var(--paper) background.");process.exit(1);}const evenRowBlock=css.match(/\.content tbody tr:nth-child\(even\) td \{[^}]*\}/);if(!evenRowBlock){console.error("Expected .content tbody tr:nth-child(even) td rule block");process.exit(1);}if(!evenRowBlock[0].includes("background: var(--paper);")){console.error("Expected striped table rows to be normalized to var(--paper).");process.exit(1);}if(evenRowBlock[0].includes("var(--table-alternate-bg)")){console.error("Expected general even-row table striping to be removed.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");if(!/\.content td p,\s*\.content th p \{[^}]*margin:\s*0;/s.test(css)){console.error("Expected table cell paragraphs to remove vertical margins.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const multirowBlock=css.match(/\.content thead tr \+ tr th \{[^}]*\}/);if(!multirowBlock){console.error("Expected .content thead tr + tr th rule block");process.exit(1);}for(const expected of ["background: rgba(56, 94, 170, 0.96);","color: #ffffff;","border-top: 2px solid rgba(255, 255, 255, 0.18);"]){if(!multirowBlock[0].includes(expected)){console.error(`Expected multi-row table header styling for: ${expected}`);process.exit(1);}}const rowspanBlock=css.match(/\.content thead th\[rowspan\] \{[^}]*\}/);if(!rowspanBlock||!rowspanBlock[0].includes("vertical-align: middle;")){console.error("Expected rowspan headers to stay vertically centered.");process.exit(1);}const splitBlock=css.match(/\.content thead th \+ th \{[^}]*\}/);if(!splitBlock||!splitBlock[0].includes("border-left-color: rgba(255, 255, 255, 0.12);")){console.error("Expected header cell dividers to be stronger for multi-row headers.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/\.content th \{[^}]*\}/);if(!block){console.error("Expected .content th rule block");process.exit(1);}for(const expected of ["background: var(--brand-blue-deep);","color: #ffffff;","font-size: 14px;"]){if(!block[0].includes(expected)){console.error(`Expected table header styling for: ${expected}`);process.exit(1);}}if(block[0].includes("rgba(241, 245, 249, 0.96)")||block[0].includes("rgba(226, 232, 240, 0.92)")){console.error("Expected .content th to stop using pale mdBook-like header backgrounds");process.exit(1);}'
check_contains theme/custom.css '.table-data-table th:first-child,'
check_contains theme/custom.css '.table-data-table td:first-child {'
check_contains theme/custom.css 'text-align: left !important;'
check_contains theme/custom.css '#table-6 .table-data-table tbody td:nth-child(-n + 3) {'
check_contains theme/custom.css 'vertical-align: middle;'
check_contains theme/custom.css '#table-6 .table-data-table colgroup col:nth-child(1) {'
check_contains theme/custom.css 'width: 15% !important;'
check_contains theme/custom.css 'width: 31% !important;'
check_contains theme/custom.css 'width: 12% !important;'
check_contains theme/custom.css 'width: 42% !important;'
check_contains theme/custom.css '#table-6 .table-data-table tbody td:nth-child(4) {'
check_contains theme/custom.css 'text-align: left !important;'
check_contains theme/custom.css '#table-6 .table-data-table tbody td:nth-child(4) ul {'
check_contains theme/custom.css '.table-6-rule-list {'
check_contains theme/custom.css 'grid-template-columns: minmax(0, 1fr) auto;'
check_contains theme/custom.css '.table-6-rule-label {'
check_contains theme/custom.css '.table-6-rule-value {'
check_contains theme/custom.css 'font-variant-numeric: tabular-nums;'
check_contains theme/custom.css '#table-6 .table-data-table thead tr:first-child th {'
check_contains theme/custom.css 'font-size: 12px;'
check_contains theme/custom.css 'letter-spacing: 0.04em;'
check_contains theme/custom.css '#table-6 .table-data-table thead tr:last-child th {'
check_contains theme/custom.css 'font-size: 13px;'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");for(const selector of ["#table-6 .table-data-table thead tr:first-child th {","#table-6 .table-data-table thead tr:last-child th {"]){const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);if(block.includes("background: rgba(239, 246, 255, 0.8);")||block.includes("background: linear-gradient(180deg, rgba(226, 232, 240, 0.92) 0%, rgba(235, 241, 249, 0.94) 100%);")){console.error(`Expected ${selector} to stop using pale table header backgrounds`);process.exit(1);}if(!block.includes("color: #ffffff;")){console.error(`Expected ${selector} to use white header text`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const block=css.match(/#table-6 \.table-data-table thead tr:last-child th \{[^}]*\}/);if(!block){console.error("Expected #table-6 second-row header rule block");process.exit(1);}if(block[0].includes("font-style: italic;")){console.error("Expected #table-6 second-row headers to stop using italic style.");process.exit(1);}if(block[0].includes("color: rgba(30, 58, 138, 0.82);")){console.error("Expected #table-6 second-row headers to stop using low-contrast blue text.");process.exit(1);}for(const expected of ["background: rgba(56, 94, 170, 0.96);","color: #ffffff;","border-top: 2px solid rgba(255, 255, 255, 0.18);"]){if(!block[0].includes(expected)){console.error(`Expected #table-6 second-row header styling for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '#table-6 .table-data-table tbody tr:nth-child(even) td {'
check_contains theme/custom.css 'background: var(--paper);'
check_not_contains theme/custom.css 'background: rgba(238, 243, 251, 0.22);'
check_contains theme/custom.css '#table-6 .table-data-table th + th,'
check_contains theme/custom.css 'border-left-color: rgba(148, 163, 184, 0.08);'
check_contains theme/custom.css 'display: table;'
check_contains theme/custom.css '.book-sidebar-shell .chapter li a {'
check_contains theme/custom.css 'padding: 8px 12px;'
check_contains theme/custom.css 'border-radius: 8px;'
check_contains theme/custom.css '.on-this-page ol,'
check_contains theme/custom.css '.on-this-page > ol,'
check_contains theme/custom.css 'padding: 0;'
check_contains theme/custom.css 'border-left: 0;'
check_not_contains theme/custom.css '@import url("https://fonts.googleapis.com'
check_contains theme/custom.js 'document.body.classList.add("book-outline-ready")'
check_contains theme/custom.js 'function installHeaderSearchSlot()'
check_not_contains theme/custom.js 'function installMobileChapterBar()'
check_not_contains theme/custom.js 'sidebarToggle.click();'
check_not_contains theme/custom.js 'sidebarToggle.checked = !sidebarToggle.checked;'
check_contains theme/custom.js 'function installInlineOutlineCard()'
check_contains theme/custom.js 'function buildMobileOutlineCardBody('
check_contains theme/custom.js 'linkWrapper.dataset.headingTag = targetHeadingElement ? targetHeadingElement.tagName.toLowerCase() : ""'
check_contains theme/custom.js 'data-heading-tag='
check_not_contains theme/custom.js 'querySelectorAll(":scope > ol > li.header-item > .chapter-link-wrapper > a")'
check_contains theme/custom.js 'className = "reader-mobile-outline-card-header"'
check_contains theme/custom.js 'className = "reader-mobile-outline-toggle"'
check_contains theme/custom.js 'function getActivePartLabel()'
check_contains theme/custom.js 'function createHeroMetaItem('
check_contains theme/custom.js 'function buildHeroMetaItems('
check_contains theme/custom.js 'function renderChapterHero('
check_contains theme/custom.js 'function installChapterHero()'
check_contains theme/custom.js 'function installOutlineReferenceSections()'
check_contains theme/custom.js 'function buildReferenceRailLabel('
check_contains theme/custom.js 'function applyReaderPageMeta('
check_contains theme/custom.js 'function balanceLeadFigureWeight()'
check_contains theme/custom.js 'function truncateReferenceText('
check_contains theme/custom.js 'displayText: buildReferenceRailLabel(label, text)'
check_contains theme/custom.js 'referenceLabel: referenceParts.label'
check_contains theme/custom.js 'referenceTitle: referenceParts.title'
check_contains theme/custom.js 'document.querySelector(".toolbar-search-slot")'
check_not_contains theme/custom.js 'document.querySelector(".reader-mobile-chapter-toggle")'
check_contains theme/custom.js 'document.querySelector(".reader-chapter-hero-anchor")'
check_contains theme/custom.js 'document.querySelector(".reader-mobile-outline-anchor")'
check_contains theme/custom.js 'document.querySelector(".book-outline-figures")'
check_contains theme/custom.js 'document.querySelector(".book-outline-tables")'
check_contains theme/custom.js 'document.querySelector(".book-outline-formulas")'
check_contains theme/custom.js 'function annotateFormulas()'
check_contains theme/custom.js 'function collectFormulaCards()'
check_contains theme/custom.js 'data-equation-label'
check_contains theme/custom.js 'data-formula-nav'
check_contains theme/custom.js 'reader-page-meta.json'
check_contains theme/custom.js 'book-outline-link book-outline-link--reference'
check_contains theme/custom.js 'book-outline-link--reference-label'
check_contains theme/custom.js 'book-outline-link--reference-title'
check_contains theme/custom.js 'title.textContent = baseTitle;'
check_not_contains theme/custom.js 'title.textContent = baseTitle + " (" + items.length + ")"'
check_contains theme/custom.js 'const searchClear = document.getElementById("mdbook-search-clear");'
check_contains theme/custom.js 'const searchresultsOuter = document.getElementById("mdbook-searchresults-outer");'
check_contains theme/custom.js 'const searchresultsHeader = document.getElementById("mdbook-searchresults-header");'
check_contains theme/custom.js 'window.search.hasFocus = function () {'
check_contains theme/custom.js 'toolbarSearchSlot.appendChild(searchresultsOuter);'
check_contains theme/custom.js 'searchClear.addEventListener("mousedown", function (event) {'
check_contains theme/custom.js 'searchClear.hidden = state.query.length === 0;'
check_contains theme/custom.js 'document.addEventListener("mousedown", handleDocumentMouseDown);'
check_contains theme/custom.js 'function handleKeyboardResults(event) {'
check_contains theme/custom.js 'highlightMarker.mark(highlight, {'
check_contains theme/custom.js 'appendHighlightedText(title, record.title || record.breadcrumbs || "Untitled", query);'
check_contains theme/custom.js 'const searchToggle = document.getElementById("mdbook-search-toggle");'
check_contains theme/custom.js 'searchWrap.classList.add("hidden");'
check_contains theme/custom.js 'searchToggle.setAttribute("aria-expanded", "false");'
check_contains theme/custom.js 'searchToggle.focus();'
check_contains theme/custom.js 'toolbarSearchSlot.classList.toggle("hidden", slotHidden)'
check_contains theme/custom.js 'requestAnimationFrame(function focusToolbarSearchbar()'
check_contains theme/custom.js 'searchbar.focus();'
check_contains theme/custom.js 'searchbar.select();'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const marker="@media (max-width: 1023px) {";const start=css.indexOf(marker);if(start===-1){console.error("Expected mobile toolbar media query.");process.exit(1);}const next=css.indexOf("\n\n@media",start + marker.length);const block=(next===-1?css.slice(start):css.slice(start,next));for(const expected of [".toolbar-actions {","display: flex;","#mdbook-search-toggle {","display: inline-flex !important;","order: 3;",".toolbar-main {","position: absolute;",".toolbar-main .toolbar-search-slot.hidden {","display: none !important;","#mdbook-menu-bar .book-toolbar .toolbar-actions .toolbar-contact-link {","display: inline-flex !important;","order: 2;",".toolbar-actions .reader-language-switch[data-reader-language-switch=\"toolbar\"] {","order: 1;",".toolbar-actions .toolbar-contact-link .toolbar-link-label {","display: none;"]){if(!block.includes(expected)){console.error(`Expected mobile search access rule ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");const start=js.indexOf("item.addEventListener(\"mouseenter\", function () {");if(start===-1){console.error("Expected mouseenter handler for search result items.");process.exit(1);}const end=js.indexOf("      });",start);if(end===-1){console.error("Expected end of mouseenter handler for search result items.");process.exit(1);}const block=js.slice(start,end);if(block.includes("renderResults();")){console.error("Search result mouseenter handler must not re-render the full results list.");process.exit(1);}'
check_not_contains theme/custom.js 'function applyPageVariants()'
check_not_contains theme/custom.js 'window.bookPageVariants'
check_contains scripts/shared/book-page-variants.mjs 'disclaimer.html'
check_contains scripts/shared/book-page-variants.mjs 'general-conclusion.html'
check_contains scripts/shared/book-page-variants.mjs 'list-of-equations.html'
check_contains scripts/shared/book-page-variants.mjs 'cover.html'
check_not_contains scripts/shared/book-page-variants.mjs 'front-matter.html'
check_contains scripts/shared/book-page-variants.mjs 'list-of-figures.html'
check_contains scripts/shared/book-page-variants.mjs 'foreword.html'
check_contains scripts/shared/book-page-variants.mjs 'general-introduction.html'
check_contains scripts/shared/book-page-variants.mjs 'chapter-11-general-conclusion.html'
check_contains scripts/shared/book-page-variants.mjs 'glossary.html'
check_contains scripts/shared/book-page-variants.mjs 'bibliographical-references.html'
check_contains scripts/shared/book-page-variants.mjs 'abbreviations-acronyms-and-abbreviations.html'
check_contains theme/custom.js 'function annotateFigureCaptions()'
check_contains theme/custom.js 'const figureCaptionRuntime = (function createFigureCaptionRuntime() {'
check_contains theme/custom.js 'function parseFigureNumber(text) {'
check_contains theme/custom.js 'function isLikelyAltDerivedCaption(text) {'
check_contains theme/custom.js 'function buildAltDerivedFigureCaption(paragraph) {'
check_contains theme/custom.js 'const altDerivedCaption = figureCaptionRuntime.buildAltDerivedFigureCaption(paragraph);'
check_not_contains theme/custom.js '/[.!?]["'"'"']?$/.test(normalized)'
check_contains theme/custom.js 'const figureVariantClasses = {'
check_contains theme/custom.js 'const wrapper = document.createElement("figure")'
check_contains theme/custom.js 'wrapper.className = "figure-card figure-anchor-target"'
check_contains theme/custom.js 'wrapper.classList.add("figure-card--multi")'
check_not_contains theme/custom.js 'figure-card--flush-media'
check_not_contains theme/custom.js 'figure-card--inset-media'
check_contains theme/custom.js 'figure-card--panel-pair'
check_contains theme/custom.js 'mediaBlock.classList.add("figure-media")'
check_contains theme/custom.js 'mediaCandidates.length > 1'
check_not_contains package.json 'upstream-atlas-reader.pdf'
check_contains theme/custom.js 'mediaGrid.className = "figure-media figure-media-grid"'
check_contains theme/custom.js 'mediaItem.className = "figure-media-item"'
check_contains theme/custom.js 'wrapper.classList.add(className);'
check_contains theme/custom.js 'captionLabel.textContent = "Figure "'
check_not_contains theme/custom.js 'captionLabel.textContent = "Figure " + match[1] + ":";'
check_contains theme/custom.js 'const header = document.createElement("div")'
check_contains theme/custom.js 'header.className = "figure-card-header"'
check_contains theme/custom.js 'captionLabel.className = "figure-card-label"'
check_contains theme/custom.js 'const footer = document.createElement("figcaption")'
check_contains theme/custom.js 'footer.className = "figure-card-footer"'
check_contains theme/custom.js 'captionText.className = "figure-card-title"'
check_contains theme/custom.js 'wrapper.appendChild(header);'
check_contains theme/custom.js 'wrapper.appendChild(footer);'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function isNarrativeFigureReference(text)","function parseFigureCaption(text)","if (isNarrativeFigureReference(normalized))","const explicitCaption = figureCaptionRuntime.parseFigureCaption(paragraph.textContent || \"\");","const altDerivedCaption = figureCaptionRuntime.buildAltDerivedFigureCaption(paragraph);"]){if(!js.includes(expected)){console.error(`Expected figure caption parsing compatibility for: ${expected}`);process.exit(1);}}'
check_contains theme/custom.js 'collectReferenceCards(".figure-card", ".figure-card-footer", ".figure-card-label", ".figure-card-title")'
check_contains theme/custom.js 'function annotateTables()'
check_contains theme/custom.js 'const tableId = "table-" +'
check_contains theme/custom.js 'wrapper.className = "table-anchor-target"'
check_contains theme/custom.js 'const tableCard = document.createElement("div")'
check_contains theme/custom.js 'tableCard.className = "table-card"'
check_contains theme/custom.js 'const tableShell = document.createElement("div")'
check_contains theme/custom.js 'tableShell.className = "table-anchor-shell"'
check_contains theme/custom.js 'const tableScroll = document.createElement("div")'
check_contains theme/custom.js 'tableScroll.className = "table-scroll"'
check_contains theme/custom.js 'const captionIcon = document.createElement("span")'
check_contains theme/custom.js 'captionIcon.className = "table-caption-icon"'
check_contains theme/custom.js 'const captionLabel = document.createElement("span")'
check_contains theme/custom.js 'captionLabel.className = "table-caption-label"'
check_contains theme/custom.js 'captionText.className = "table-caption-text"'
check_contains theme/custom.js 'caption.className = "table-caption"'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");if(!js.includes("function parseTableCaption(text)")){console.error("Expected parseTableCaption helper in theme/custom.js");process.exit(1);}const expected=String.raw`.match(/^(?:Table|Tableau)\s+(\d+)(?:\s*:\s*|\s+)(.*)$/i);`;if(!js.includes(expected)){console.error("Expected table caption parsing to support both colon and colonless captions.");process.exit(1);}'
check_contains theme/custom.js 'wrapper.dataset.captionPosition = captionPosition'
check_contains theme/custom.js 'wrapper.appendChild(tableCard);'
check_contains theme/custom.js 'tableCard.appendChild(caption);'
check_contains theme/custom.js 'tableCard.appendChild(tableShell);'
check_contains theme/custom.js 'tableCard.appendChild(notesGroup);'
check_not_contains theme/custom.js 'wrapper.appendChild(caption);'
check_not_contains theme/custom.js 'wrapper.appendChild(notesGroup);'
check_contains theme/custom.js 'function collectTableNotes('
check_contains theme/custom.js 'function enhanceTable6()'
check_contains theme/custom.js 'function installCrossReferenceLinks()'
check_contains theme/custom.js 'document.querySelectorAll(".reader-article p, .reader-article li")'
check_contains theme/custom.js 'document.getElementById("figure-" + referenceNumber)'
check_contains theme/custom.js 'document.getElementById("table-" + referenceNumber)'
check_contains theme/custom.js 'element.closest(".figure-card, .table-anchor-target, .formula-anchor-target, .reference-index")'
check_contains theme/custom.js 'installCrossReferenceLinks();'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");const expected=`document.querySelectorAll(".reader-sidebar-row--chapter[href]")`;if(!js.includes(expected)){console.error("Expected chapter-route lookup in theme/custom.js");process.exit(1);}'
check_contains theme/custom.js 'document.getElementById("formula-" + formulaAnchorLabel)'
check_contains editions/en/book.toml 'additional-js = ["theme/ga.js", "theme/custom.js"]'
check_contains editions/fr/book.toml 'additional-js = ["theme/ga.js", "theme/custom.js"]'
check_not_contains editions/en/book.toml 'theme/vendor/panzoom.min.js'
check_not_contains editions/fr/book.toml 'theme/vendor/panzoom.min.js'
check_contains theme/custom.js 'function installFigureImageOpenLinks()'
check_contains theme/custom.js 'document.querySelectorAll(".reader-article .figure-card img")'
check_contains theme/custom.js 'window.open(imageUrl, "_blank", "noopener")'
check_contains theme/custom.js 'event.key === "Enter" || event.key === " "'
check_contains theme/custom.css '.figure-card-image--zoom-link:focus-visible {'
check_not_contains theme/custom.js 'window.Panzoom || window.panzoom'
check_not_contains theme/custom.css '.figure-viewer {'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");const expected=String.raw`/\b(Figure)\s+(\d+)\b|\b(Table|Tableau)\s+(\d+)\b|\b(Section)\s+(\d+(?:\.\d+)*)\b|\b(Chapter|Chapitre)\s+(\d+)\b|\b(Equation|Formula|Équation|Formule)\s+(\d+(?:\.\d+)*)\b/g`;if(!js.includes(expected)){console.error("Expected reader cross-reference matcher in theme/custom.js");process.exit(1);}'
check_contains theme/custom.js 'function parseTable6Rule(text)'
check_contains theme/custom.js 'ruleList.className = "table-6-rule-list"'
check_contains theme/custom.js 'ruleItem.className = "table-6-rule-item"'
check_contains theme/custom.js 'label.className = "table-6-rule-label"'
check_contains theme/custom.js 'value.className = "table-6-rule-value"'
check_contains theme/custom.js 'function buildOutlineList('
check_contains theme/custom.js 'querySelector("#mdbook-sidebar mdbook-sidebar-scrollbox .chapter-item > .on-this-page")'
check_contains theme/custom.js 'querySelectorAll("a.header-in-summary")'
check_contains theme/custom.js 'document.getElementById("mdbook-reader-scroll")'
check_not_contains theme/custom.js 'const englishDefaultChapterPath = "chapters/disclaimer.html";'
check_not_contains theme/custom.js 'const frenchDefaultChapterPath = "chapters/foreword.html";'
check_not_contains theme/custom.js 'window.location.replace(target.href)'
check_contains public/book/chapters/chapter-01-general-introduction.html 'class="reader-sidebar-projection"'
check_contains public/book/chapters/chapter-01-general-introduction.html 'class="sidebar book-sidebar-shell book-sidebar-shell--projected"'
check_contains public/book/chapters/chapter-01-general-introduction.html 'reader-sidebar-row reader-sidebar-row--chapter reader-sidebar-row--active'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'class="reader-sidebar-projection"'
check_contains public/book/chapters/chapter-08-west-african-fiscal-regimes.html 'class="sidebar book-sidebar-shell book-sidebar-shell--projected"'
check_not_contains public/book/chapters/glossary.html 'class="book-sidebar-utility-link-icon"'
check_not_contains public/book/chapters/list-of-figures.html 'class="book-sidebar-utility-link-icon"'
check_not_contains public/book/index.html 'class="book-shell-grid"'
check_not_contains public/book/index.html 'class="book-page-surface"'
check_not_contains public/book/index.html 'class="book-main-column"'
check_contains public/book/index.html 'class="reader-sidebar-projection"'
check_contains public/book/index.html 'class="sidebar book-sidebar-shell book-sidebar-shell--projected"'
check_contains public/book/index.html 'reader-sidebar-row reader-sidebar-row--reference reader-sidebar-row--active'
check_contains public/book/index.html 'reader-sidebar-row-title">Cover</span>'
check_not_contains public/book/index.html 'book-outline-shell'
check_not_contains public/book/index.html 'toolbar-center'
check_not_contains public/book/index.html 'book-toolbar-actions'
check_contains theme/custom.css '.book-sidebar-shell {'
check_contains theme/custom.css 'display: flex;'
check_contains theme/custom.css 'flex-direction: column;'
check_contains theme/custom.css '.reader-sidebar-scroll {'
check_not_contains theme/custom.css 'top: var(--sidebar-intro-height);'
check_not_contains theme/custom.css '--sidebar-intro-height: 0px;'
check_not_contains theme/custom.js 'sidebarShellResizeObserver'
check_not_contains theme/custom.js 'function syncSidebarShellGeometry()'
check_not_contains theme/custom.js 'function installSidebarShellGeometry()'
check_not_contains theme/custom.js '"--sidebar-intro-height"'

echo "Site render checks passed."
check_not_contains theme/custom.css '.reader-sidebar-section-chevron'
check_not_contains theme/custom.js 'reader-sidebar-section-chevron'
check_not_contains theme/custom.js 'function buildSidebarSectionChevron('
check_not_contains theme/index.hbs 'reader-sidebar-section-chevron'
check_not_contains theme/index.hbs 'function buildSidebarSectionChevron('
