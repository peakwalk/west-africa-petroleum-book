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

check_file_size_at_most() {
  file_path="$1"
  max_bytes="$2"
  size_bytes="$(wc -c < "$file_path" | tr -d ' ')"

  if [ "$size_bytes" -gt "$max_bytes" ]; then
    echo "Expected $file_path to be <= $max_bytes bytes but was $size_bytes bytes" >&2
    exit 1
  fi
}

check_image_has_no_opaque_white_fringe() {
  file_path="$1"
  max_pixels="$2"
  fringe_pixels="$(magick "$file_path" -crop 430x110+170+25 +repage -format '%[fx:mean*w*h]' -channel RGBA -fx '(a>0.05 && r>0.92 && g>0.92 && b>0.92)?1:0' info: | cut -d. -f1)"

  if [ "$fringe_pixels" -gt "$max_pixels" ]; then
    echo "Expected $file_path to have <= $max_pixels opaque white pixels but found $fringe_pixels" >&2
    exit 1
  fi
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
check_exists src/images/figure-002.webp
check_exists src/images/figure-003-trimmed.webp
check_exists src/images/figure-004.webp
check_exists src/images/figure-004-oil-cuts-transparent.webp
check_exists src/images/figure-005-upstream-phases-transparent.webp
check_exists src/images/figure-006-block-assignment-transparent.webp
check_exists src/images/figure-006.webp
check_exists src/images/figure-007.webp
check_exists src/images/figure-008.webp
check_exists src/images/figure-009.webp
check_exists src/images/figure-011.webp
check_exists src/images/figure-012.webp
check_exists src/images/figure-013.webp
check_exists src/images/figure-014.webp
check_exists src/images/figure-015.webp
check_exists src/images/figure-016.webp
check_exists src/images/figure-019.webp
check_exists src/images/figure-020.webp
check_exists src/images/figure-017.webp
check_exists src/images/figure-021.webp
check_exists src/images/figure-022.svg
check_exists src/images/figure-023.webp
check_exists src/images/figure-026.svg
check_exists src/images/figure-030.svg
check_exists src/images/figure-024.webp
check_exists src/images/figure-025.webp
check_exists src/images/figure-027.webp
check_exists src/images/figure-028.webp
check_exists src/images/figure-029.webp
check_exists src/images/figure-031.webp
check_exists src/images/figure-032.webp
check_exists src/images/figure-001.webp
check_exists src/images/figure-003-trimmed.png
check_exists assets/images/west-africa-intelligence-overlay.svg
check_exists assets/images/upstream-atlas-nav-logo.webp
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
check_exists assets/icons/homepage-cropped/icon-research.png
check_exists assets/icons/homepage-cropped/icon-industry-monitoring.png
check_exists assets/icons/homepage-cropped/icon-intelligence.png
check_exists assets/icons/homepage-cropped/icon-production.png
check_exists assets/icons/homepage-cropped/icon-exploration.png
check_exists assets/icons/homepage-cropped/icon-fiscal.png
check_exists assets/icons/homepage-cropped/icon-regulation.png
check_exists assets/icons/homepage-cropped/icon-audience-research.png
check_exists assets/icons/homepage-cropped/icon-audience-policy.png
check_exists assets/icons/homepage-cropped/icon-audience-operators.png
check_exists assets/icons/homepage/icon-audience-research.svg
check_exists assets/icons/homepage/icon-audience-policy.svg
check_exists assets/icons/homepage/icon-audience-operators.svg
check_exists assets/icons/homepage-sprite.svg
check_exists scripts/build_reader_page_meta.mjs
check_contains package.json '"build:index": "node scripts/generate-index-page.mjs"'
check_contains package.json '"build:legal": "node scripts/generate-legal-pages.mjs"'
check_contains package.json '"build:reader-meta": "node scripts/build_reader_page_meta.mjs"'
check_contains package.json '"build:site": "rm -rf public && mkdir -p public && npm run build:index && npm run build:legal && npm run build:chapters'
check_contains package.json '&& npm run build:reader-meta"'
check_contains .github/workflows/pages.yml 'run: npm run build:site'
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
check_not_contains book.toml 'git-repository-url = "https://github.com/peakwalk/west-africa-petroleum-book"'
check_not_contains book.toml 'edit-url-template = "https://github.com/peakwalk/west-africa-petroleum-book/edit/main/{path}"'

check_contains public/index.html 'class="landing-shell"'
check_contains public/index.html 'class="hero-panel"'
check_contains public/index.html 'class="chapter-preview-card"'
check_contains public/index.html 'class="site-header-inner"'
check_contains public/index.html 'upstream-atlas-favicon.png?v=2'
check_contains public/index.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/index.html 'upstream-atlas-nav-logo.png'
check_contains public/index.html 'upstream-atlas-icon.png'
check_contains public/index.html 'href="chapters/"'
check_contains public/index.html 'class="current-link" href="/">Home</a>'
check_contains public/index.html 'href="#countries">Countries</a>'
check_contains public/index.html 'href="#about">About</a>'
check_contains public/index.html 'href="#resources">Resources</a>'
check_order public/index.html 'href="#about">About</a>' 'href="#resources">Resources</a>'
check_contains public/index.html 'class="header-contact-link"'
check_contains public/index.html 'mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas'
check_contains public/index.html 'aria-label="Contact Us"'
check_not_contains public/index.html 'class="nav-search"'
check_not_contains public/index.html 'href="book/toc.html"'
check_not_contains public/index.html 'section-heading section-heading-centered'
check_contains public/index.html 'West African Petroleum Intelligence'
check_contains public/index.html 'West African upstream intelligence built on a rigorous reference base.'
check_contains public/index.html 'rigorous upstream reference base'
check_contains public/index.html 'Reference book'
check_contains public/index.html 'Available now'
check_contains public/index.html 'In build'
check_contains public/index.html 'Platform Intelligence'
check_contains public/index.html 'Coming Soon'
check_contains public/index.html 'class="feature-card-icon ua-icon-image ua-icon-image--feature"'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-research.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-industry-monitoring.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-intelligence.png'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-start-reading'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-menu'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-close'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-production.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-exploration.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-fiscal.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-regulation.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-research.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-policy.png'
check_contains public/index.html 'assets/icons/homepage-cropped/icon-audience-operators.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-start-reading.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-menu.png'
check_not_contains public/index.html 'assets/icons/homepage-cropped/icon-close.png'
check_contains public/index.html 'class="button-icon ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm"'
check_not_contains public/index.html 'class="mobile-nav-contact"'
check_not_contains public/index.html '>Contact Us</a>'
check_contains public/index.html 'class="reference-evidence-grid"'
check_contains public/index.html 'Country reserves'
check_contains public/index.html 'Country Intelligence'
check_contains public/index.html 'class="country-card country-card-compact"'
check_contains public/index.html 'Additional markets'
check_contains public/index.html 'class="country-card-top"'
check_contains public/index.html 'class="country-card-badge"'
check_contains public/index.html 'class="country-signal-grid"'
check_contains public/index.html 'class="country-signal-icon ua-icon-image ua-icon-image--signal"'
check_contains public/index.html 'class="country-signal-copy"'
check_contains public/index.html 'class="country-signal-value"'
check_contains public/index.html 'Template ready'
check_contains public/index.html 'Brief queued'
check_contains public/index.html 'Signals planned'
check_contains public/index.html 'class="chapters-link-row"'
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
check_exists public/assets/icons/homepage-cropped/icon-research.png
check_exists public/assets/icons/homepage-cropped/icon-industry-monitoring.png
check_exists public/assets/icons/homepage-cropped/icon-intelligence.png
check_exists public/assets/icons/homepage-cropped/icon-production.png
check_exists public/assets/icons/homepage-cropped/icon-exploration.png
check_exists public/assets/icons/homepage-cropped/icon-fiscal.png
check_exists public/assets/icons/homepage-cropped/icon-regulation.png
check_exists public/assets/icons/homepage-cropped/icon-audience-research.png
check_exists public/assets/icons/homepage-cropped/icon-audience-policy.png
check_exists public/assets/icons/homepage-cropped/icon-audience-operators.png
check_exists public/assets/icons/homepage/icon-audience-research.svg
check_exists public/assets/icons/homepage/icon-audience-policy.svg
check_exists public/assets/icons/homepage/icon-audience-operators.svg
check_exists public/assets/icons/homepage-sprite.svg
check_exists public/assets/images/upstream-atlas-nav-logo.webp
check_file_size_at_most public/assets/images/upstream-atlas-icon.png 50000
check_file_size_at_most public/assets/images/upstream-atlas-wordmark.png 110000
check_file_size_at_most public/assets/images/upstream-atlas-nav-logo.webp 80000
check_image_has_no_opaque_white_fringe public/assets/images/upstream-atlas-nav-logo.webp 50
check_file_size_at_most public/assets/images/prototype-hero.jpg 120000
check_contains assets/css/landing.css '--page-bg: #f7f8f9;'
check_contains assets/css/landing.css '--surface-muted: #eef2f4;'
check_contains assets/css/landing.css '--ink-primary: #0b1f33;'
check_contains assets/css/landing.css '--brand-blue: #3163c2;'
check_contains assets/css/landing.css '--brand-blue-deep: #264d97;'
check_contains assets/css/landing.css '--footer-bg: #0b1f33;'
check_contains assets/css/landing.css '--secondary: #d88a1d;'
check_contains assets/css/landing.css '--text: var(--ink-primary);'
check_contains assets/css/landing.css 'opacity: 0.28;'
check_contains assets/css/landing.css 'background: linear-gradient(135deg, rgba(38, 77, 151, 0.82) 0%, rgba(11, 31, 51, 0.84) 100%);'
check_contains assets/css/landing.css 'background: var(--brand-blue-deep);'
check_contains assets/css/landing.css 'background: url("../images/prototype-hero.jpg") center right / cover;'
check_contains assets/css/landing.css 'background: url("../images/west-africa-intelligence-overlay.svg") center / cover no-repeat;'
check_contains assets/css/landing.css 'opacity: 0.09;'
check_not_contains assets/css/landing.css '--primary: #264d97;'
check_contains assets/css/landing.css '@media (min-width: 901px) {'
check_contains assets/css/landing.css '.hero-signal-panel {'
check_contains assets/css/landing.css 'margin-top: clamp(17rem, 30vw, 20.5rem);'
check_contains assets/css/landing.css '.chapters-link-row {'
check_contains assets/css/landing.css 'width: min(76rem, calc(100% - 2rem));'
check_contains assets/css/landing.css '.chapters-link {'
check_contains assets/css/landing.css 'margin: 0;'
check_contains assets/css/landing.css 'border-radius: 0.5rem;'
check_contains assets/css/landing.css 'font-weight: 500;'
check_contains assets/css/landing.css '.brand-mark-image {'
check_contains assets/css/landing.css '.brand-mark-image-compact {'
check_not_contains assets/css/landing.css '.footer-brand-surface {'
check_contains assets/css/landing.css 'font-family: "Manrope", "Inter", sans-serif;'
check_contains assets/css/landing.css '.mobile-nav-toggle {'
check_contains assets/css/landing.css '.mobile-nav-toggle .mobile-nav-icon-close {'
check_contains assets/css/landing.css '.header-actions {'
check_contains assets/css/landing.css '.header-contact-link::after {'
check_contains assets/css/landing.css '.mobile-nav-contact {'
check_contains assets/css/landing.css '.ua-icon {'
check_contains assets/css/landing.css '.ua-icon-image {'
check_contains assets/css/landing.css '.ua-icon--feature {'
check_contains assets/css/landing.css '.ua-icon-image--feature {'
check_contains assets/css/landing.css '.ua-icon-image--signal {'
check_contains assets/css/landing.css '.feature-card-icon {'
check_contains assets/css/landing.css '.button-icon {'
check_contains assets/css/landing.css '.mobile-nav-icon-close {'
check_contains assets/css/landing.css '.mobile-nav-menu\[open\] .mobile-nav-toggle .mobile-nav-icon-close {'
check_contains assets/css/landing.css '.country-signal-icon {'
check_contains assets/css/landing.css '.country-signal-copy {'
check_contains assets/css/landing.css '.ua-icon--audience {'
check_contains assets/css/landing.css '@media (max-width: 700px) {'
check_contains assets/css/landing.css '.site-header-inner {'
check_contains assets/css/landing.css 'grid-template-columns: auto auto;'
check_contains assets/css/landing.css '@media (max-width: 360px) {'
check_contains assets/css/landing.css '.brand-mark-image-full {'
check_contains assets/css/landing.css '.mobile-nav-toggle .button-label {'
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
check_contains public/chapters/index.html 'class="button button-header" href="../book/">'
check_contains public/chapters/index.html '<span class="button-label">Start Reading</span>'
check_contains public/chapters/index.html '../assets/icons/homepage-sprite.svg#icon-start-reading'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-start-reading.png'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-menu.png'
check_not_contains public/chapters/index.html '../assets/icons/homepage-cropped/icon-close.png'
check_contains public/chapters/index.html 'class="current-link" href="./">Chapters</a>'
check_contains public/chapters/index.html 'href="../#countries">Countries</a>'
check_contains public/chapters/index.html 'href="../#about">About</a>'
check_contains public/chapters/index.html 'href="../#resources">Resources</a>'
check_order public/chapters/index.html 'href="../#about">About</a>' 'href="../#resources">Resources</a>'
check_contains public/chapters/index.html 'class="header-contact-link"'
check_contains public/chapters/index.html 'mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas'
check_not_contains public/chapters/index.html 'class="mobile-nav-contact"'
check_not_contains public/chapters/index.html '>Contact Us</a>'
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
check_contains public/chapters/index.html '<h2>Part I: General Information on the Oil Industry</h2>'
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
check_contains public/chapters/index.html 'General Information on the Oil Industry'
check_contains public/chapters/index.html '../book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html'

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
check_contains public/terms-of-use.html 'href="index.html"'
check_contains public/terms-of-use.html 'upstream-atlas-nav-logo.webp'
check_contains public/privacy-policy.html 'upstream-atlas-nav-logo.webp'
check_contains public/cookie-policy.html 'upstream-atlas-nav-logo.webp'
check_not_contains public/terms-of-use.html 'upstream-atlas-nav-logo.png'
check_not_contains public/privacy-policy.html 'upstream-atlas-nav-logo.png'
check_not_contains public/cookie-policy.html 'upstream-atlas-nav-logo.png'
check_not_contains public/terms-of-use.html 'legal-page-brand-copy'
check_not_contains public/privacy-policy.html 'legal-page-brand-copy'
check_not_contains public/cookie-policy.html 'legal-page-brand-copy'
check_not_contains public/terms-of-use.html 'href="/"'
check_order public/terms-of-use.html '<a href="index.html#about">About</a>' '<p class="site-footer-heading">Resources</p>'

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
check_contains public/book/index.html 'class="toolbar-search-slot hidden"'
check_contains public/book/index.html 'id="mdbook-search-wrapper" class="hidden"'
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
check_contains public/book/reader-page-meta.json 'chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html'
check_order public/book/index.html 'css/general-' 'theme/custom-'
check_not_contains public/book/toc.html 'href="index.html" target="_parent">Home</a>'
check_not_contains public/book/print.html 'title="Git repository"'
check_not_contains public/book/404.html 'title="Git repository"'
check_tree_not_contains public/book 'https://github.com/peakwalk/west-africa-petroleum-book'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'reader-layout'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'reader-main'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'reader-outline'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'reader-article'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'class="book-sidebar-download"'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'href="../../assets/book/upstream-atlas-reader.pdf"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-024.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-024.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-030.svg'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-030.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-031.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-031.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-032.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-032.png'
check_not_contains public/book/chapters/bibliographical-references.html 'TABLE OF CONTENTS'
check_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-002-a.webp'
check_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-002-b.webp'
check_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003-map.jpg'
check_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-004-oil-cuts-transparent.webp'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-002.png'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003.png'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-003-trimmed.png'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md 'figure-004.png'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md '0 to 80-100°C'
check_not_contains src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md '120 to 180°C'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-005-upstream-phases-transparent.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-006-block-assignment-transparent.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-007.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-007-b.webp'
check_order src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-006-block-assignment-transparent.webp' 'figure-007.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-008.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-009.jpg'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-010-em.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-011-system.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-012-geoseismic.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-013-anticline.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-014-traps.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-015-depth-map.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-a.jpg'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016-b.jpg'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-017.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-018-model.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-019.webp'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-020.webp'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-006.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-007.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-008.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-009.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-011.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-012.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-013.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-014.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-015.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-016.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-017.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-017.svg'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-019.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-019.svg'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'figure-020.png'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'Multiple qv streamers'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md '![Figure 009](../images/figure-009.webp)'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'Authorization to operate'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'Exploration Authorization'
check_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-021.webp'
check_not_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-021.png'
node -e 'const fs=require("fs");const text=fs.readFileSync("src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md","utf8");const img21=text.indexOf("![Figure 021](../images/figure-021.webp)");const cap21=text.indexOf("Figure 21: Economic Value");const img22=text.indexOf("![Figure 022](../images/figure-022.svg)");const cap22=text.indexOf("Figure 22: Distribution of income from production");if(img21===-1||cap21===-1||img21>cap21){console.error("Expected Figure 21 image to appear before its caption in chapter 3");process.exit(1);}if(img22===-1||cap22===-1||img22>cap22){console.error("Expected Figure 22 image to appear before its caption in chapter 3");process.exit(1);}'
check_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-022.svg'
check_not_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-022.png'
check_not_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-022.webp'
check_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-023.webp'
check_not_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-023.png'
check_not_contains src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md 'figure-023.svg'
for figure in 025 027 028 029; do
  check_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.webp"
  check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.png"
  check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.svg"
done
for figure in 024 031 032; do
  check_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.webp"
  check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.png"
  check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md "figure-${figure}.svg"
done
check_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'figure-026.svg'
check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'figure-026.png'
check_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'figure-030.svg'
check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md 'figure-030.png'
check_contains src/SUMMARY.md 'chapters/cover.md'
check_contains src/chapters/cover.md 'figure-001.webp'
check_not_contains src/chapters/cover.md 'figure-001.png'
check_contains public/book/chapters/cover.html 'class="book-cover"'
check_contains public/book/chapters/cover.html 'class="book-cover-frame"'
check_contains public/book/chapters/cover.html 'class="book-cover-kicker"'
check_contains public/book/chapters/cover.html 'class="book-cover-title"'
check_contains public/book/chapters/cover.html 'class="book-cover-subtitle"'
check_contains public/book/chapters/cover.html 'class="book-cover-figure"'
check_contains public/book/chapters/cover.html 'class="book-cover-footer"'
check_contains public/book/chapters/cover.html 'class="book-cover-imprint"'
check_contains public/book/chapters/cover.html 'class="book-cover-entry"'
check_contains public/book/chapters/cover.html 'class="book-cover-entry-link"'
check_contains public/book/chapters/cover.html 'Start reading'
check_contains public/book/chapters/cover.html 'href="../chapters/foreword.html"'
check_contains public/book/chapters/cover.html 'figure-001.webp'
check_not_contains public/book/chapters/cover.html 'figure-001.png'
check_contains public/book/index.html 'class="book-cover-entry-link"'
check_contains public/book/index.html 'src="images/figure-001.webp"'
check_contains public/book/index.html 'href="chapters/foreword.html"'
check_not_contains public/book/index.html 'src="../images/figure-001.webp"'
check_not_contains public/book/index.html 'href="../chapters/foreword.html"'
check_contains public/book/chapters/cover.html 'function applyInitialBookPageVariant()'
check_contains public/book/chapters/cover.html 'document.body.classList.add("book-page-cover")'
check_order public/book/chapters/cover.html 'document.body.classList.add("book-page-cover")' 'id="mdbook-content" class="content reader-layout"'
check_contains public/book/chapters/front-matter.html 'http-equiv="refresh"'
check_contains public/book/chapters/front-matter.html 'url=cover.html'
check_contains public/book/chapters/front-matter.html 'window.location.replace(target)'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-002-a.webp'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-002-b.webp'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003-map.jpg'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-004-oil-cuts-transparent.webp'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '30.031<sup>1</sup>'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '<p><sup>1</sup> Data Ministries</p>'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '<p><sup>2</sup> RPS Energy Report, 2006</p>'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-002.png'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003.png'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-003-trimmed.png'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'figure-004.png'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '<p>0 to 80-100°C</p>'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html '<p>120 to 180°C</p>'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-005-upstream-phases-transparent.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-006-block-assignment-transparent.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-007.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-007-b.webp'
check_order public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-006-block-assignment-transparent.webp' 'figure-007.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-008.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-009.jpg'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-010-em.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-011-system.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-012-geoseismic.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-013-anticline.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-014-traps.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-015-depth-map.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-a.jpg'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016-b.jpg'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-019.webp'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-020.webp'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<p>Authorization to operate</p>'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<p>Exploration Authorization</p>'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-006.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-007.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-008.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-009.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-011.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-012.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-013.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-014.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-015.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-016.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-019.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-019.svg'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-020.png'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<p>Multiple qv streamers</p>'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'figure-009.webp'
check_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-021.webp'
check_not_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-021.png'
check_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-022.svg'
check_not_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-022.png'
check_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-023.webp'
check_not_contains public/book/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html 'figure-023.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-025.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-025.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-027.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-027.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-028.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-028.png'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-029.webp'
check_not_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'figure-029.png'
check_contains public/book/chapters/cover.html 'Exploration and Exploitation of Petroleum Resources in West Africa'
check_contains public/book/chapters/cover.html 'Roles and responsibilities of States and analysis of tax regimes'
check_contains public/book/chapters/cover.html 'Upstream Atlas Reference Edition'
check_contains public/book/chapters/cover.html 'Digital Reading Edition'
check_file_size_at_most public/book/images/figure-017.webp 100000
check_file_size_at_most public/book/images/figure-018.jpg 200000
check_contains public/book/chapters/list-of-figures.html 'List of Figures'
check_contains public/book/chapters/list-of-figures.html 'class="reference-index reference-index-figures"'
check_contains public/book/chapters/list-of-figures.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/list-of-figures.html 'chapter-01-value-chain-of-the-hydrocarbon-sector.html#figure-1'
check_contains public/book/chapters/list-of-figures.html 'chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html#figure-32'
check_contains public/book/chapters/list-of-tables.html 'List of Tables'
check_contains public/book/chapters/list-of-tables.html 'class="reference-index reference-index-tables"'
check_contains public/book/chapters/list-of-tables.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/list-of-tables.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/list-of-tables.html 'chapter-01-value-chain-of-the-hydrocarbon-sector.html#table-1'
check_contains public/book/chapters/list-of-tables.html 'chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html#table-11'
check_not_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md '<blockquote>'
check_contains src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md '<caption><p>Table 8: State'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html","utf8");const table7Start=html.indexOf("<p>Table 7:");const table8Start=html.indexOf("<p>Table 8:");if(table7Start===-1||table8Start===-1){console.error("Expected Table 7 and Table 8 markers in chapter 4 HTML.");process.exit(1);}const table7Block=html.slice(table7Start,table8Start);if(table7Block.includes("<blockquote>")){console.error("Expected Table 7 numeric cells to render without blockquote wrappers.");process.exit(1);}for(const expected of [">35<",">50<",">30<"]){if(!table7Block.includes(expected)){console.error(`Expected Table 7 to preserve value ${expected}.`);process.exit(1);}}'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'Abbreviations, Acronyms and Abbreviations'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="reference-index reference-index-abbreviations"'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="chapter-nav-card chapter-nav-previous"'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="chapter-nav-card chapter-nav-next"'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'class="reference-glossary-list"'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'ABEX'
check_contains public/book/chapters/abbreviations-acronyms-and-abbreviations.html 'AfCFTA'
check_contains public/book/chapters/glossary.html 'class="book-formula api-density-formula"'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/glossary.html","utf8");if(!/API\s*density\s*=/.test(html)||!/Density\s*at\s*15°C/.test(html)||!html.includes("141.5")||!html.includes("131.5")||html.includes("Densité")||html.includes("141,5")||html.includes("131,5")){console.error("Expected glossary formula to use English density terms and decimal points");process.exit(1);}'
check_not_contains public/book/chapters/glossary.html 'language-math'
check_order public/book/chapters/glossary.html 'It is calculated by the formula:' 'class="book-formula api-density-formula"'
check_order public/book/chapters/glossary.html 'class="book-formula api-density-formula"' 'Light oil (API &gt; 30°)'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'data-equation-label="2.1"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'data-equation-label="2.2"'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'data-equation-label="2.3"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-group formula-group--prospect" data-equation-label="2.1"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-where formula-where--grid formula-where--prospect" aria-label="Prospect formula definitions"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-where formula-where--grid formula-where--volumetric" aria-label="Volumetric assessment formula definitions"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-group formula-group--volumetric" data-equation-label="2.2"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md '<p class="formula-where-label">with:</p>'
check_not_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md '<p class="formula-where-label">where:</p>'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-spec-grid formula-spec-grid--two formula-spec-grid--volumetric"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'class="formula-case-note"'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'formula-where-term">P(prospect):'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'formula-where-term">FVF:'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'formula-note-term">GOR:'
check_contains src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md 'formula-note-term">CGR:'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html","utf8");const normalize=(value)=>value.replace(/<[^>]+>/g," ").replace(/&nbsp;/g," ").replace(/\u00a0/g," ").replace(/&minus;/g,"-").replace(/[−–]/g,"-").replace(/&times;/g,"x").replace(/&deg;/g,"°").replace(/\s+/g," ").trim();const text=normalize(html);const labels=[...html.matchAll(/data-equation-label=\"([^\"]+)\"/g)].map((match)=>match[1]);if(labels.join(",")!=="2.1,2.2"){console.error(`Expected chapter 2 primary equation labels 2.1,2.2 but found ${labels.join(",")}`);process.exit(1);}for(const expected of ["P(prospect) = P(source rock) x P(reservoir) x P(trap)","VHcP = GRV x N/G x Ø x Shc x 1/FVF","FVF = Reservoir Volume/Surface Volume"]){if(!text.includes(expected)){console.error(`Expected chapter 2 primary formula content for: ${expected}`);process.exit(1);}}for(const forbidden of ["Equation 2.3","Equation 2.3a","Equation 2.3b","Formula 2.3a","Formula 2.3b"]){if(text.includes(forbidden)){console.error(`Did not expect chapter 2 extra equation label: ${forbidden}`);process.exit(1);}}'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<p class="formula-where-label">with:</p>'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<p class="formula-where-label">where:</p>'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-group formula-group--prospect" data-equation-label="2.1"'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-group formula-group--volumetric" data-equation-label="2.2"'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html","utf8");const start=html.indexOf("class=\"formula-where formula-where--grid formula-where--volumetric\"");const end=html.indexOf("class=\"formula-derivation formula-derivation--volumetric\"",start);if(start===-1||end===-1){console.error("Expected chapter 2 volumetric formula-where block bounds");process.exit(1);}const block=html.slice(start,end);for(const forbidden of ["<pre><code>","&lt;div class=\"book-formula book-formula--local\"","&lt;p class=\"formula-where-item\""]){if(block.includes(forbidden)){console.error(`Did not expect escaped raw HTML inside volumetric formula-where block: ${forbidden}`);process.exit(1);}}for(const expected of ["IBCs = ∑Deposit Area x Deposit Thickness","Porosity (Ø) = Pore Volume (Vv)/ Reservoir Volume (V)","Shc = 1-Sw","FVF = Reservoir Volume/Surface Volume"]){if(!block.includes(expected)){console.error(`Expected rendered local formula content inside formula-where block for: ${expected}`);process.exit(1);}}'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-spec-grid formula-spec-grid--two formula-spec-grid--volumetric"'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-derivation formula-derivation--volumetric"'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-grid"'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">For the oil'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">For gas'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-connector">Thus'
check_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-note"'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">Oil case'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-title">Gas case'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html 'class="formula-case-connector">leads to'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<li><strong>For the oil</strong></li>'
check_not_contains public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html '<li><strong>For gas</strong></li>'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html","utf8");const start=html.indexOf("class=\"formula-derivation formula-derivation--volumetric\"");const end=html.indexOf("<p>A lead ranking is performed",start);if(start===-1||end===-1){console.error("Expected chapter 2 formula derivation block bounds");process.exit(1);}const block=html.slice(start,end);const caseCount=(block.match(/<section class=\"formula-case\"/g)||[]).length;if(caseCount!==2){console.error(`Expected 2 formula cases in derivation block but found ${caseCount}`);process.exit(1);}for(const forbidden of ["<pre","language-html","&lt;section","class=&quot;formula-case&quot;"]){if(block.includes(forbidden)){console.error(`Unexpected escaped or code-rendered formula markup: ${forbidden}`);process.exit(1);}}'
node -e 'const fs=require("fs");const html=fs.readFileSync("public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html","utf8");const normalize=(value)=>value.replace(/<[^>]+>/g," ").replace(/&nbsp;/g," ").replace(/\u00a0/g," ").replace(/&minus;/g,"-").replace(/[−–]/g,"-").replace(/&times;/g,"x").replace(/&deg;/g,"°").replace(/\s+/g," ").trim();const text=normalize(html);const labels=[...html.matchAll(/data-equation-label=\"([^\"]+)\"/g)].map((match)=>match[1]);if(labels.join(",")!=="4.1,4.2,4.3"){console.error(`Expected chapter 4 primary equation labels 4.1,4.2,4.3 but found ${labels.join(",")}`);process.exit(1);}for(const expected of ["Post Royalty Revenue = Gross Revenue - Royalty","Oil Profit = Gross Revenue - Royalty - Recoverable Costs","R-Factor=Cumulative Net Revenue/Cumulative Costs"]){if(!text.includes(expected)){console.error(`Expected chapter 4 formula content for: ${expected}`);process.exit(1);}}if(!/<div class=\"book-formula\" data-equation-label=\"4\.1\"/.test(html)){console.error("Expected post-royalty formula to be promoted to numbered formula 4.1.");process.exit(1);}const splitMatch=html.match(/<section class=\"formula-group formula-group--split formula-group--oil-profit\"[\s\S]*?<\/section>/);if(!splitMatch){console.error("Expected chapter 4 split oil-profit formula group");process.exit(1);}const split=splitMatch[0];const normalizedSplit=normalize(split);if(!/data-equation-label=\"4\.2\"/.test(split)){console.error("Expected oil-profit formula group to be renumbered as 4.2.");process.exit(1);}for(const expected of ["class=\"formula-split-divider\"","class=\"book-formula-bridge\">or<"]){if(!split.includes(expected)){console.error(`Expected split oil-profit structure for: ${expected}`);process.exit(1);}}for(const expected of ["Oil Profit = Revenue Post Royalty - Recoverable Costs","Oil Profit = Gross Revenue - Royalty - Recoverable Costs"]){if(!normalizedSplit.includes(expected)){console.error(`Expected split oil-profit structure for: ${expected}`);process.exit(1);}}const panelMatch=html.match(/<section class=\"formula-panel formula-panel--r-factor\"[\s\S]*?<\/section>/);if(!panelMatch){console.error("Expected chapter 4 grouped R-factor formula panel");process.exit(1);}const panel=panelMatch[0];if(!/data-equation-label=\"4\.3\"/.test(panel)){console.error("Expected grouped R-factor panel to be renumbered as 4.3.");process.exit(1);}for(const label of ["a)","b)","c)","d)"]){if(!panel.includes(`data-formula-label=\"${label}\"`)){console.error(`Expected chapter 4 R-factor label ${label}`);process.exit(1);}}const normalizedPanel=normalize(panel);for(const formula of ["R-Factor=Cumulative Revenue/Cumulative Cost","R-Factor = (Cumulative Revenue - Cumulative Opex) / Cumulative Capex","R-Factor = (Cumulative Revenues - Cumulative Profits) / (Cumulative Investments + Cumulative Opex)","R-Factor=Cumulative Net Revenue/Cumulative Costs"]){if(!normalizedPanel.includes(formula)){console.error(`Expected grouped R-factor panel content for: ${formula}`);process.exit(1);}}for(const forbidden of ["data-equation-label=\"4.4\"","data-equation-label=\"4.5\"","Formula 4.4"]){if(html.includes(forbidden)||text.includes(forbidden)){console.error(`Did not expect extra chapter 4 primary equation label: ${forbidden}`);process.exit(1);}}'
check_contains public/book/toc.html 'List of Figures'
check_contains public/book/toc.html 'List of Tables'
check_contains public/book/toc.html 'Abbreviations, Acronyms and Abbreviations'
check_not_contains public/book/index.html 'site-footer-detailed'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'site-footer-detailed'
check_contains public/book/index.html 'upstream-atlas-favicon.png?v=2'
check_not_contains public/book/index.html 'fonts.googleapis.com'
check_not_contains public/book/index.html 'fonts.gstatic.com'

# Reader shell contract
check_contains public/book/index.html 'rel="preload" href="reader-fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin'
check_contains public/book/index.html 'rel="preload" href="reader-fonts/literata-var.woff2" as="font" type="font/woff2" crossorigin'
check_contains public/book/chapters/cover.html 'rel="preload" href="../reader-fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin'
check_contains public/book/chapters/cover.html 'rel="preload" href="../reader-fonts/literata-var.woff2" as="font" type="font/woff2" crossorigin'
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
check_contains theme/custom.css '@media (max-width: 900px) {'
check_not_contains theme/custom.css '.book-home-label {'
check_contains theme/custom.css '.toolbar-search-slot {'
check_contains theme/custom.css '.toolbar-search-slot.hidden {'
check_contains theme/custom.css 'width: min(100%, var(--toolbar-search-width));'
check_contains theme/custom.css 'max-width: var(--toolbar-search-width);'
check_contains theme/custom.css '.toolbar-search-slot #mdbook-searchbar-outer {'
check_contains theme/custom.css '#mdbook-search-overlay-root .searchresults-outer {'
check_contains theme/custom.css '.toolbar-search-slot #mdbook-searchbar {'
check_contains theme/custom.css '#mdbook-searchbar::placeholder {'
check_contains theme/custom.css '.toolbar-actions .toolbar-contact-link:hover,'
check_contains theme/custom.css 'position: fixed;'
check_contains theme/custom.css 'inset-inline-start: auto;'
check_contains theme/custom.css 'inset-inline-end: calc(16px + var(--toolbar-contact-width) + var(--toolbar-utility-gap));'
check_contains theme/custom.css 'width: min(100vw - 2rem, var(--toolbar-search-width));'
check_contains theme/custom.css 'top: calc(var(--menu-bar-height) + 12px);'
check_contains theme/custom.css 'max-width: calc(100vw - 2rem);'
check_contains theme/custom.css 'max-height: calc(100dvh - var(--menu-bar-height) - 2rem);'
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
check_contains theme/custom.css '--sidebar-intro-height:'
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
check_contains theme/index.hbs '<div class="toolbar-search-slot hidden" aria-hidden="true"></div>'
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
check_contains theme/index.hbs 'function applyInitialBookPageVariant()'
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
  [".reader-sidebar-row {", ["grid-template-columns: 2.25rem minmax(0, 1fr);", "gap: 0.625rem;", "width: 100%;", "padding: 0.5rem 1.75rem 0.5rem 0.75rem;", "border-radius: 0.75rem;", "color: var(--sidebar-fg);", "box-sizing: border-box;"]],
  [".reader-sidebar-row-index {", ["color: currentColor;", "font-size: 0.6875rem;", "letter-spacing: 0.14em;"]],
  [".reader-sidebar-row-title {", ["display: block;", "width: 100%;", "font-family: var(--reader-sans);", "font-size: 0.8125rem;", "line-height: 1.45;"]],
  [".reader-sidebar-row--reference {", ["padding: 0.4rem 1.25rem 0.4rem 0.75rem;", "border-radius: 0.5rem;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-row--reference {", ["padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);"]],
  [".reader-sidebar-row--reference.reader-sidebar-row--with-icon {", ["grid-template-columns: 1.375rem minmax(0, 1fr);", "gap: 0.5rem;"]],
  [".reader-sidebar-row--reference .reader-sidebar-row-title {", ["font-size: 0.8125rem;", "line-height: 1.45;"]],
  [".reader-sidebar-row-icon {", ["width: 1.375rem;", "height: 1.375rem;", "border-radius: 999px;"]],
  [".reader-sidebar-row:hover,", ["border-color: rgba(49, 99, 194, 0.12);", "background: rgba(49, 99, 194, 0.06);", "color: var(--sidebar-fg);"]],
  [".reader-sidebar-row--reference.reader-sidebar-row--active {", ["padding: 0.4rem 1.25rem 0.4rem 0.75rem;"]],
  [".reader-sidebar-section--front-matter .reader-sidebar-row--reference.reader-sidebar-row--active {", ["padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);"]],
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
const narrowHeader = slice("@media (max-width: 900px) {", "@media (min-width: 768px) {");

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
  "padding: 0.5rem 1.75rem 0.5rem 0.75rem;",
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
  "padding: 0.4rem 1.25rem 0.4rem 0.75rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-row--reference {",
  "padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);",
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
  "padding: 0.4rem 1.25rem 0.4rem 0.75rem;",
  ".reader-sidebar-section--front-matter .reader-sidebar-row--reference.reader-sidebar-row--active {",
  "padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);",
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
  "grid-template-columns: auto 1fr;",
  ".toolbar-main,",
  ".toolbar-actions {",
  "display: none;",
  ".toolbar-sidebar {",
  "gap: 1rem;",
  "padding-inline-end: 0;",
  ".book-home-icon-full {",
  "display: block;",
  "width: var(--reader-logo-width-narrow);",
  ".book-home-icon-compact {",
  "display: none;",
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
  "width: max-content;",
  "min-width: 100%;",
]) {
  if (!formulaLineRule[0].includes(expected)) {
    console.error(`Expected volumetric formula line CSS to include ${expected}`);
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
const mobileReaderEnd = css.indexOf("@media (max-width: 900px) {", mobileReaderStart);
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
node -e 'const fs=require("fs");const hbs=fs.readFileSync("theme/index.hbs","utf8");for(const expected of ["function bootstrapSidebarProjection()","projection.dataset.projectionSignature = projectionSignature;","sidebar.classList.add(\"book-sidebar-shell--projected\");","customElements.whenDefined(\"mdbook-sidebar-scrollbox\")"]){if(!hbs.includes(expected)){console.error(`Expected theme/index.hbs to include ${expected}`);process.exit(1);}}const navIndex=hbs.indexOf("<nav id=\"mdbook-sidebar\"");const bootstrapIndex=hbs.indexOf("function bootstrapSidebarProjection()");const pageIndex=hbs.indexOf("<div id=\"mdbook-page-wrapper\"");if(navIndex===-1||bootstrapIndex===-1||pageIndex===-1||!(navIndex < bootstrapIndex && bootstrapIndex < pageIndex)){console.error("Expected sidebar projection bootstrap script to run immediately after the sidebar markup and before the page wrapper renders.");process.exit(1);}'
node -e 'const fs=require("fs");const hbs=fs.readFileSync("theme/index.hbs","utf8");for(const expected of ["const intro = sidebar.querySelector(\".book-sidebar-intro\");","sidebar.style.setProperty(\"--sidebar-intro-height\", intro.offsetHeight + \"px\");"]){if(!hbs.includes(expected)){console.error(`Expected theme/index.hbs to include ${expected}`);process.exit(1);}}const introHeightIndex=hbs.indexOf("sidebar.style.setProperty(\"--sidebar-intro-height\", intro.offsetHeight + \"px\");");const projectedIndex=hbs.indexOf("sidebar.classList.add(\"book-sidebar-shell--projected\");");if(introHeightIndex===-1||projectedIndex===-1||!(introHeightIndex < projectedIndex)){console.error("Expected inline sidebar geometry sync to happen before projected sidebar activation.");process.exit(1);}'
node -e 'const fs=require("fs");const hbs=fs.readFileSync("theme/index.hbs","utf8");if(hbs.includes("sessionStorage.removeItem(\"reader-sidebar-scroll-offset\");")){console.error("Expected inline sidebar bootstrap to preserve reader-sidebar-scroll-offset until runtime hydration can reconcile any late raw TOC mutations.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const chapterLink=block(".book-sidebar-shell .chapter li a {");for(const expected of ["font-size: 0.875rem;","line-height: 1.4286;"]){if(!chapterLink.includes(expected)){console.error(`Expected .book-sidebar-shell .chapter li a to include ${expected}`);process.exit(1);}}if(chapterLink.includes("font-size: 14px;")||chapterLink.includes("line-height: 20px;")||chapterLink.includes("font-size: 1.4rem;")||chapterLink.includes("line-height: 2rem;")){console.error("Expected .book-sidebar-shell .chapter li a to use repo-owned typography calibrated for the explicit /book root font contract");process.exit(1);}const partTitle=block(".book-sidebar-shell .chapter li.part-title {");if(!partTitle.includes("font-size: 0.75rem;")){console.error("Expected .book-sidebar-shell .chapter li.part-title to include font-size: 0.75rem;");process.exit(1);}if(partTitle.includes("font-size: 12px;")||partTitle.includes("font-size: 1.2rem;")){console.error("Expected .book-sidebar-shell .chapter li.part-title to stop using legacy sizing under the explicit /book root font contract");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const bookTitle=block(".book-sidebar-book-title {");if(!bookTitle.includes("color: var(--sidebar-fg);")){console.error("Expected .book-sidebar-book-title to align with the normal sidebar navigation text color.");process.exit(1);}const frontBackTitle=block(".reader-sidebar-section--front-matter .reader-sidebar-section-title,");if(!frontBackTitle.includes("color: var(--sidebar-fg);")){console.error("Expected Front Matter and Back Matter section titles to align with the normal sidebar navigation text color.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const sectionHeader=block(".reader-sidebar-section-header {");if(sectionHeader.includes("line-height: 25%;")){console.error("Expected sidebar section headers to stop relying on line-height: 25% for visual alignment; use explicit layout instead.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".reader-sidebar-section--front-matter .reader-sidebar-section-body,");if(start===-1){console.error("Expected Front Matter body selector to remain present in theme/custom.css");process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error("Expected closing brace for Front Matter body selector block");process.exit(1);}const frontMatterBody=css.slice(start,end+1);if(frontMatterBody.includes("padding-inline-start:")){console.error("Expected Front Matter body container position to remain unchanged; use row padding instead of container padding.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const activeRow=block(".reader-sidebar-row--active {");if(activeRow.includes("padding-inline-end:")){console.error("Expected active sidebar rows to preserve the same inline geometry as inactive rows; reserve the indicator gutter in the base row instead of shifting active items.");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const visitedRow=block(".reader-sidebar-row:link,");for(const expected of ["color: var(--sidebar-fg);","-webkit-text-fill-color: var(--sidebar-fg);"]){if(!visitedRow.includes(expected)){console.error(`Expected reader sidebar normal link/visited contract to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");if(!js.includes(`sessionStorage.setItem("sidebar-scroll-offset"`)){console.error("Expected projected sidebar links to persist sidebar-scroll-offset before navigation so mdBook can restore the same vertical viewport.");process.exit(1);}if(!js.includes(`sessionStorage.setItem("reader-sidebar-scroll-offset"`)){console.error("Expected projected sidebar links to persist a projection-owned reader-sidebar-scroll-offset contract before navigation.");process.exit(1);}if(!js.includes(`sessionStorage.getItem("reader-sidebar-scroll-offset"`)){console.error("Expected projected sidebar install to read back the projection-owned reader-sidebar-scroll-offset contract.");process.exit(1);}const start=js.indexOf("function installSidebarProjection() {");const end=js.indexOf("\n\n  function buildOutlineList(",start);if(start===-1||end===-1){console.error("Expected installSidebarProjection block in theme/custom.js");process.exit(1);}const block=js.slice(start,end);if(block.includes("revealActiveSidebarTarget(scrollContainer);")){console.error("Expected installSidebarProjection to stop re-scrolling the visible sidebar shell after mdBook already restored sidebar position.");process.exit(1);}if(!block.includes("scrollContainer.scrollTop = scrollbox.scrollTop;")){console.error("Expected installSidebarProjection to adopt the raw mdBook scrollbox scrollTop before hiding it.");process.exit(1);}if(!block.includes("scrollContainer.scrollTop += currentOffset - storedProjectionOffset;")){console.error("Expected installSidebarProjection to preserve the clicked projection row offset across page navigations before falling back to raw mdBook scroll restoration.");process.exit(1);}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");if(!js.includes("const storedProjectionOffset = readAndClearSidebarProjectionOffset();")){console.error("Expected installSidebarProjection to always reconcile any pending reader-sidebar-scroll-offset contract during runtime hydration.");process.exit(1);}if(js.includes("const storedProjectionOffset = projectionChanged ? readAndClearSidebarProjectionOffset() : null;")){console.error("Expected installSidebarProjection to stop skipping reader-sidebar-scroll-offset reconciliation when the early bootstrap projection already exists.");process.exit(1);}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");const start=js.indexOf("function syncOutlineRailVisibility() {");const end=js.indexOf("\n\n  function syncOutlineActiveState()",start);if(start===-1||end===-1){console.error("Expected syncOutlineRailVisibility() to manage the empty right-rail contract.");process.exit(1);}const block=js.slice(start,end);for(const expected of ["document.querySelector(\"#mdbook-outline-scroll\")","document.querySelector(\".book-outline-body .on-this-page\")","document.querySelector(\".book-outline-figures\")","document.querySelector(\".book-outline-tables\")","document.querySelector(\".book-outline-formulas\")","document.body.classList.toggle(\"book-outline-empty\", !hasVisibleOutlineContent);","outline.hidden = !hasVisibleOutlineContent;"]){if(!block.includes(expected)){console.error(`Expected syncOutlineRailVisibility() to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");function block(selector){const start=css.indexOf(selector);if(start===-1){console.error(`Expected selector block: ${selector}`);process.exit(1);}const end=css.indexOf("}",start);if(end===-1){console.error(`Expected closing brace for selector block: ${selector}`);process.exit(1);}return css.slice(start,end+1);}const layout=block("body.book-outline-empty .reader-layout {");if(!layout.includes("grid-template-columns: minmax(0, 1fr);")){console.error("Expected empty outline pages to collapse the reader layout back to a single content column.");process.exit(1);}const rail=block("body.book-outline-empty .reader-outline {");if(!rail.includes("display: none;")){console.error("Expected empty outline pages to hide the desktop right rail entirely.");process.exit(1);}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function bindSidebarProjectionRowInteraction(","if (row.dataset.readerSidebarBound === \"true\") {","row.dataset.readerSidebarBound = \"true\";","hydrateSidebarProjectionRows(projection);"]){if(!js.includes(expected)){console.error(`Expected theme/custom.js to include ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function installSidebarDisplayStateSync()","function syncSidebarDisplayState()","if (!sidebarToggle.checked) {","if (sidebar.style.display === \"none\") {","sidebar.style.display = \"\";","sidebar.offsetHeight;","sidebar.setAttribute(\"aria-hidden\", \"false\");","requestAnimationFrame(syncSidebarDisplayState);","installSidebarDisplayStateSync();"]){if(!js.includes(expected)){console.error(`Expected theme/custom.js to include ${expected}`);process.exit(1);}}const applyIndex=js.indexOf("applyPageVariants();");const displayIndex=js.indexOf("installSidebarDisplayStateSync();");const shellIndex=js.indexOf("installSidebarShellGeometry();");if(applyIndex===-1||displayIndex===-1||shellIndex===-1||!(applyIndex<displayIndex&&displayIndex<shellIndex)){console.error("Expected sidebar display-state sync to run after page variants and before sidebar geometry/projection work.");process.exit(1);}'
check_contains theme/custom.js 'new ResizeObserver'
check_contains theme/custom.js '--sidebar-intro-height'
check_contains theme/custom.js 'reader-sidebar-scroll'
check_not_contains theme/custom.js '--sidebar-utilities-height'
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
check_contains theme/custom.js 'general-conclusion.html'
check_contains theme/custom.js 'glossary.html'
check_contains theme/custom.js 'bibliographical-references.html'
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
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const sharedHeadingBlocks=[...css.matchAll(/\.reader-article h2,\s*\.reader-article h3,\s*\.reader-article h4,\s*\.reader-article h5,\s*\.reader-article h6 \{[^}]*\}/g)].map((match)=>match[0]);const sharedHeadingBlock=sharedHeadingBlocks.find((block)=>block.includes("margin-inline: auto;"));if(!sharedHeadingBlock){console.error("Expected shared reader heading positioning rule block.");process.exit(1);}for(const expected of ["position: relative;","margin-inline: auto;"]){if(!sharedHeadingBlock.includes(expected)){console.error(`Expected shared reader heading positioning rule to include ${expected}`);process.exit(1);}}const h2Match=css.match(/\.reader-article h2 \{[^}]*\}/);if(!h2Match||!h2Match[0].includes("max-width: calc(var(--reader-article-body-measure) * var(--reader-h2-body-align-scale));")){console.error("Expected h2 headings to scale body measure by the h2 alignment ratio.");process.exit(1);}const h3Matches=[...css.matchAll(/\.reader-article h3,\s*\.reader-article h4,\s*\.reader-article h5,\s*\.reader-article h6 \{[^}]*\}/g)].map((match)=>match[0]);const h3MeasureBlock=h3Matches.find((block)=>block.includes("max-width: calc(var(--reader-article-body-measure) * var(--reader-h3-body-align-scale));"));if(!h3MeasureBlock){console.error("Expected h3-h6 headings to scale body measure by the subheading alignment ratio.");process.exit(1);}const anchorSelector=".reader-article a.header.reader-heading-link--indexed,";const anchorStart=css.indexOf(anchorSelector);const anchorEnd=css.indexOf("}",anchorStart);if(anchorStart===-1||anchorEnd===-1){console.error(`Expected rule block for ${anchorSelector}`);process.exit(1);}const anchorBlock=css.slice(anchorStart,anchorEnd+1);for(const expected of ["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.85rem;","align-items: start;","width: 100%;","max-width: 100%;"]){if(!anchorBlock.includes(expected)){console.error(`Expected ${anchorSelector} to include ${expected}`);process.exit(1);}}const indexSelector=".reader-article a.header.reader-heading-link--indexed .reader-heading-index {";const indexStart=css.indexOf(indexSelector);const indexEnd=css.indexOf("}",indexStart);if(indexStart===-1||indexEnd===-1){console.error(`Expected rule block for ${indexSelector}`);process.exit(1);}const indexBlock=css.slice(indexStart,indexEnd+1);for(const expected of ["position: relative;","text-align: start;"]){if(!indexBlock.includes(expected)){console.error(`Expected ${indexSelector} to include ${expected}`);process.exit(1);}}for(const removed of ["position: absolute;","right: calc(100% + 0.85rem);","text-align: right;"]){if(indexBlock.includes(removed)){console.error(`Expected ${indexSelector} to remove ${removed}`);process.exit(1);}}const selector=".reader-article a.header.reader-heading-link--indexed .reader-heading-title {";const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);for(const expected of ["display: block;","max-width: var(--reader-heading-measure);","width: 100%;","text-wrap: balance;"]){if(!block.includes(expected)){console.error(`Expected ${selector} to include ${expected}`);process.exit(1);}}'
check_contains theme/custom.css '.content table {'
node -e 'const fs=require("fs");const js=fs.readFileSync("theme/custom.js","utf8");for(const expected of ["function normalizeHeadingDisplayText(text)","function splitHeadingDisplayText(text)","function renderIndexedHeadingAnchor(anchor, text)","function renderOutlineHeadingAnchor(anchor, text)","anchor.dataset.readerHeadingDisplayText = normalizedText;","document.querySelectorAll(\".reader-article a.header\")","renderIndexedHeadingAnchor(anchor, anchor.textContent);","renderOutlineHeadingAnchor(","entry.marker.classList.toggle(\"book-outline-active-marker--visible\", isActive);"]){if(!js.includes(expected)){console.error(`Expected heading hyphen cleanup behavior for: ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const checks=[["\n.reader-chapter-hero {",["display: grid;","width: min(100%, var(--reader-article-body-measure));","margin-inline: auto;"]],[".reader-chapter-hero .reader-chapter-eyebrow {",["display: inline-flex;","justify-self: start;","padding: 0.45rem 0.85rem;","background: linear-gradient(180deg, rgba(255, 250, 240, 0.98) 0%, rgba(248, 238, 210, 0.94) 100%);","color: var(--brand-gold);","font-family: var(--reader-sans);","font-size: 12px;","letter-spacing: 0.12em;"]],[".reader-chapter-hero h1 {",["font-size: 48px;","line-height: 1.08;","max-width: var(--reader-chapter-title-measure);","text-wrap: balance;"]],[".reader-article h1:target::before,",["display: none;","content: none;"]],[".reader-article a.header.reader-heading-link--indexed,",["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.85rem;","align-items: start;","color: var(--ink);","text-decoration: none;"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-index {",["position: relative;","padding-bottom: 0.8rem;","color: var(--brand-blue);","text-align: start;","white-space: nowrap;"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-index::after {",["width: 100%;","height: 4px;","background: var(--brand-gold);"]],[".reader-article a.header.reader-heading-link--indexed .reader-heading-title {",["display: block;","min-width: 0;"]],[".reader-chapter-rule {",["width: 32px;","height: 3px;","justify-self: start;"]],[".reader-chapter-meta-item {",["font-size: 14px;"]],[".book-outline-label {",["color: var(--links);"]],[".book-outline-section-title {",["color: var(--links);"]],[".book-outline-link,",["color: var(--ink);"]],[".book-outline-link--active,",["color: var(--ink);","font-weight: 600;"]],[".reader-outline {",["min-width: 0;","overflow-x: clip;"]],[".book-outline-inner {",["gap: 2rem;","min-width: 0;"]],[".book-outline-section {",["gap: 1.25rem;","padding-top: 2rem;"]],[".reader-outline .book-outline-link:link,",["color: var(--ink);"]],[".reader-outline .book-outline-link--indexed,",["display: grid;","grid-template-columns: auto minmax(0, 1fr);","column-gap: 0.48rem;"]],[".reader-outline .book-outline-link--indexed .book-outline-heading-index {",["margin-right: 0;","white-space: nowrap;","color: var(--links);"]],[".reader-outline .book-outline-link--indexed .book-outline-heading-title {",["color: var(--ink);"]],[".on-this-page a.active,",["color: var(--ink);","font-weight: 600;"]],[".on-this-page {",["--book-outline-font-size: 13px;","--book-outline-line-height: 1.25;","--book-outline-marker-size: 0.4375rem;","--book-outline-marker-gap: 0.4rem;","min-width: 0;"]],[".on-this-page .chapter-link-wrapper {",["position: relative;","display: block;","width: 100%;","min-width: 0;","box-sizing: border-box;"]],[".on-this-page li.header-item {",["min-width: 0;"]],[".on-this-page .chapter-link-wrapper[data-heading-tag=\"h3\"] {",["padding-inline-start: 1rem;"]],[".on-this-page .chapter-link-wrapper[data-heading-tag=\"h4\"] {",["padding-inline-start: 2rem;"]],[".on-this-page a:focus-visible,",["color: var(--ink);"]],[".reader-mobile-outline-card {",["padding: 14px 16px;","border-radius: 14px;"]],[".reader-mobile-outline-card-header {",["display: flex;","justify-content: space-between;"]],[".reader-mobile-outline-toggle {",["font-size: 0.875rem;","font-weight: 600;"]],[".reader-mobile-outline-card .on-this-page > ol {",["display: flex;","flex-wrap: wrap;","gap: 0.75rem 1rem;"]],[".reader-mobile-outline-card .on-this-page li.header-item {",["min-width: 0;","max-width: 100%;"]],[".book-outline-active-marker {",["display: flex;","position: absolute;","inset-inline-start: calc(-1 * (var(--book-outline-marker-size) + var(--book-outline-marker-gap)));","top: calc((var(--book-outline-font-size) * var(--book-outline-line-height) - var(--book-outline-marker-size)) / 2);","height: var(--book-outline-marker-size);","opacity: 0;"]],[".book-outline-active-marker--visible {",["opacity: 1;"]],[".book-outline-link--indexed .book-outline-heading-index {",["margin-right: 0.24rem;"]]];for(const [selector,expected] of checks){const start=css.indexOf(selector);const end=css.indexOf("}",start);if(start===-1||end===-1){console.error(`Expected rule block for ${selector}`);process.exit(1);}const block=css.slice(start,end+1);for(const value of expected){if(!block.includes(value)){console.error(`Expected ${selector} to include ${value}`);process.exit(1);}}if(selector === ".reader-chapter-hero .reader-chapter-eyebrow {" && block.includes("border-radius:")){console.error("Expected .reader-chapter-eyebrow to remove rounded corners");process.exit(1);}}for(const removed of [".reader-mobile-chapter-toggle {",".reader-mobile-chapter-kicker {",".reader-mobile-chapter-title {"]){if(css.includes(removed)){console.error(`Expected mobile chapter selector styles to be removed: ${removed}`);process.exit(1);}}const heroTitleBlocks=[...css.matchAll(/\.reader-chapter-hero h1 \{[^}]*\}/g)].map((match)=>match[0]);if(heroTitleBlocks.length===0){console.error("Expected chapter hero title rule blocks");process.exit(1);}for(const block of heroTitleBlocks){if(!block.includes("font-size: 48px;")){console.error("Expected every chapter hero title rule block to use font-size: 48px;");process.exit(1);}if(!block.includes("max-width: var(--reader-chapter-title-measure);")){console.error("Expected every chapter hero title rule block to use the shared chapter title measure.");process.exit(1);}if(block.includes("font-size: clamp(")){console.error("Expected chapter hero title size to use fixed 48px instead of clamp");process.exit(1);}}'
check_contains theme/custom.css '.reader-article table,'
check_contains theme/custom.css 'font-family: var(--reader-sans);'
check_contains theme/custom.css 'font-size: 14px;'
check_contains theme/custom.css 'body.book-page-cover .reader-layout {'
check_contains theme/custom.css 'body.book-page-cover .reader-outline {'
check_contains theme/custom.css 'body.book-page-cover .chapter-pagination {'
check_contains theme/custom.css 'body.book-page-aux-index {'
check_not_contains theme/custom.css 'body.book-page-aux-index .reader-layout {'
check_contains theme/custom.css 'body.book-page-aux-index .reader-article {'
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
check_contains theme/custom.css '.reference-glossary-list {'
check_not_contains theme/custom.css '.reference-index-list li::marker {'
check_contains theme/custom.css '.reference-glossary-item {'
check_contains theme/custom.css '.reader-article .book-formula {'
check_contains theme/custom.css '.book-formula-line {'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const start=css.indexOf(".book-formula-line {");const end=css.indexOf("}\n\n.book-formula-bridge",start);if(start===-1||end===-1){console.error("Expected .book-formula-line rule block");process.exit(1);}const block=css.slice(start,end+1);if(!block.includes("font-style: normal;")){console.error("Expected .book-formula-line to use normal font style");process.exit(1);}if(block.includes("font-style: italic;")){console.error("Did not expect .book-formula-line to keep italic font style");process.exit(1);}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const bridgeStart=css.indexOf(".book-formula-bridge {");const bridgeEnd=css.indexOf("}\n\n.formula-anchor-target",bridgeStart);if(bridgeStart===-1||bridgeEnd===-1){console.error("Expected .book-formula-bridge rule block");process.exit(1);}const bridgeBlock=css.slice(bridgeStart,bridgeEnd+1);for(const expected of ["text-align: left;","color: rgba(15, 23, 42, 0.86);","font-size: 0.92rem;","font-weight: 800;","letter-spacing: 0.16em;"]){if(!bridgeBlock.includes(expected)){console.error(`Expected formula bridge styling for: ${expected}`);process.exit(1);}}'
node -e 'const fs=require("fs");const css=fs.readFileSync("theme/custom.css","utf8");const singleStart=css.indexOf(".reader-article .book-formula {");const singleEnd=css.indexOf("}\n\n.reader-article .book-formula:not(.api-density-formula)",singleStart);const outerStart=css.indexOf(".reader-article .book-formula:not(.api-density-formula) {");const outerEnd=css.indexOf("}\n\n.reader-article .api-density-formula",outerStart);const prospectStart=css.indexOf(".formula-group--prospect > .book-formula,");const prospectEnd=css.indexOf("}\n\n.formula-group--prospect > .book-formula .book-formula-line,",prospectStart);const splitStart=css.indexOf(".formula-group--split > .formula-split-entry > .book-formula {");const splitEnd=css.indexOf("}\n\n.formula-group--split > .formula-split-entry:first-child > .book-formula",splitStart);const panelStart=css.indexOf(".formula-panel .book-formula--panel-row {");const panelEnd=css.indexOf("}\n\n.formula-panel .book-formula--panel-row::before",panelStart);if(singleStart===-1||singleEnd===-1||outerStart===-1||outerEnd===-1||prospectStart===-1||prospectEnd===-1||splitStart===-1||splitEnd===-1||panelStart===-1||panelEnd===-1){console.error("Expected formula rule blocks");process.exit(1);}const singleBlock=css.slice(singleStart,singleEnd+1);const outerBlock=css.slice(outerStart,outerEnd+1);const prospectBlock=css.slice(prospectStart,prospectEnd+1);const splitBlock=css.slice(splitStart,splitEnd+1);const panelBlock=css.slice(panelStart,panelEnd+1);for(const [name,block,expected] of [["single",singleBlock,["font-size: 16px;","line-height: 1.2;"]],["prospect",prospectBlock,["font-size: 16px;","line-height: 1.2;"]],["split",splitBlock,["font-size: 16px;","line-height: 1.28;"]],["panel",panelBlock,["font-size: 16px;","line-height: 1.28;"]]]){for(const value of expected){if(!block.includes(value)){console.error(`Expected ${name} formulas to include ${value}`);process.exit(1);}}}for(const expected of ["margin: 24px 0 22px;"]){if(!singleBlock.includes(expected)){console.error(`Expected standalone formula block to include ${expected}`);process.exit(1);}}for(const expected of ["justify-items: start;","text-align: left;"]){if(!outerBlock.includes(expected)){console.error(`Expected standalone non-table formula alignment for ${expected}`);process.exit(1);}}for(const forbidden of ["margin: 24px auto 22px;","justify-items: center;","text-align: center;"]){if(singleBlock.includes(forbidden)||outerBlock.includes(forbidden)){console.error(`Did not expect standalone non-table formulas to include ${forbidden}`);process.exit(1);}}'
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
node -e "const fs=require('fs');const js=fs.readFileSync('theme/custom.js','utf8');if(!js.includes('captionLabel.textContent = \"Figure \" + match[1];')){console.error('Expected figure labels to render without a trailing colon.');process.exit(1);}if(js.includes('captionLabel.textContent = \"Figure \" + match[1] + \":\";')){console.error('Expected figure labels to stop rendering a trailing colon.');process.exit(1);}"
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
check_contains theme/custom.js 'const searchresultsOuter = document.getElementById("mdbook-searchresults-outer");'
check_contains theme/custom.js 'const searchOverlayRoot = document.getElementById("mdbook-search-overlay-root");'
check_contains theme/custom.js 'searchOverlayRoot.appendChild(searchresultsOuter);'
check_contains theme/custom.js 'function hideSearchResultsOverlay()'
check_contains theme/custom.js 'searchbar.addEventListener("input", function () {'
check_contains theme/custom.js 'if (searchbar.value.trim() === "") {'
check_contains theme/custom.js 'searchbar.addEventListener("keydown", function (event) {'
check_contains theme/custom.js 'if (event.key === "Escape") {'
check_contains theme/custom.js 'event.stopPropagation();'
check_contains theme/custom.js 'const searchToggle = document.getElementById("mdbook-search-toggle");'
check_contains theme/custom.js 'searchWrap.classList.add("hidden");'
check_contains theme/custom.js 'searchToggle.setAttribute("aria-expanded", "false");'
check_contains theme/custom.js 'searchToggle.focus();'
check_contains theme/custom.js 'toolbarSearchSlot.classList.toggle("hidden", slotHidden)'
check_contains theme/custom.js 'requestAnimationFrame(function focusToolbarSearchbar()'
check_contains theme/custom.js 'searchbar.focus();'
check_contains theme/custom.js 'searchbar.select();'
check_contains theme/custom.js 'function applyPageVariants()'
check_contains theme/custom.js 'cover.html'
check_not_contains theme/custom.js 'front-matter.html'
check_contains theme/custom.js 'list-of-figures.html'
check_contains theme/custom.js 'abbreviations-acronyms-and-abbreviations.html'
check_contains theme/custom.js 'document.body.classList.add("book-page-cover")'
check_contains theme/custom.js 'function annotateFigureCaptions()'
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
check_contains theme/custom.js 'wrapper.dataset.captionPosition = captionPosition'
check_contains theme/custom.js 'wrapper.appendChild(tableCard);'
check_contains theme/custom.js 'tableCard.appendChild(caption);'
check_contains theme/custom.js 'tableCard.appendChild(tableShell);'
check_contains theme/custom.js 'tableCard.appendChild(notesGroup);'
check_not_contains theme/custom.js 'wrapper.appendChild(caption);'
check_not_contains theme/custom.js 'wrapper.appendChild(notesGroup);'
check_contains theme/custom.js 'function collectTableNotes('
check_contains theme/custom.js 'function enhanceTable6()'
check_contains theme/custom.js 'function parseTable6Rule(text)'
check_contains theme/custom.js 'ruleList.className = "table-6-rule-list"'
check_contains theme/custom.js 'ruleItem.className = "table-6-rule-item"'
check_contains theme/custom.js 'label.className = "table-6-rule-label"'
check_contains theme/custom.js 'value.className = "table-6-rule-value"'
check_contains theme/custom.js 'function buildOutlineList('
check_contains theme/custom.js 'querySelector("#mdbook-sidebar mdbook-sidebar-scrollbox .chapter-item > .on-this-page")'
check_contains theme/custom.js 'querySelectorAll("a.header-in-summary")'
check_contains theme/custom.js 'document.getElementById("mdbook-reader-scroll")'
check_contains theme/custom.js 'chapters/foreword.html'
check_contains theme/custom.js 'window.location.replace(target.href)'
check_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'class="reader-sidebar-projection"'
check_contains public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html 'class="reader-sidebar-projection"'
check_not_contains public/book/chapters/glossary.html 'class="book-sidebar-utility-link-icon"'
check_not_contains public/book/chapters/list-of-figures.html 'class="book-sidebar-utility-link-icon"'
check_not_contains public/book/index.html 'class="book-shell-grid"'
check_not_contains public/book/index.html 'class="book-page-surface"'
check_not_contains public/book/index.html 'class="book-main-column"'
check_contains public/book/index.html 'class="reader-sidebar-projection"'
check_not_contains public/book/index.html 'book-outline-shell'
check_not_contains public/book/index.html 'toolbar-center'
check_not_contains public/book/index.html 'book-toolbar-actions'

echo "Site render checks passed."
check_not_contains theme/custom.css '.reader-sidebar-section-chevron'
check_not_contains theme/custom.js 'reader-sidebar-section-chevron'
check_not_contains theme/custom.js 'function buildSidebarSectionChevron('
check_not_contains theme/index.hbs 'reader-sidebar-section-chevron'
check_not_contains theme/index.hbs 'function buildSidebarSectionChevron('
