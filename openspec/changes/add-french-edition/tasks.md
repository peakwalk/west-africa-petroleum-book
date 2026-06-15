## 1. Establish edition inputs and source topology

- [x] 1.1 Add canonical English and French DOCX/PDF alias paths under a stable `resources/editions/` layout and document them in the shared edition registry.
- [x] 1.2 Add the shared edition registry plus per-edition locale catalogs for route prefixes, source roots, manuscript aliases, figure roots, and localized UI labels.
- [x] 1.3 Create the French source tree with mirrored chapter slugs, mirrored legal page keys, mirrored figure numbering, and translated landing/legal/book content placeholders or finalized copy.

## 2. Refactor public-page generation for localized editions

- [x] 2.1 Make `scripts/shared/landing-shell.mjs` locale-aware for links, navigation labels, CTA copy, footer copy, legal links, and a visible header-level language switch with edition-peer targets.
- [x] 2.2 Refactor `scripts/generate-index-page.mjs`, `scripts/generate-legal-pages.mjs`, and `scripts/generate-chapters-page.mjs` to render both editions from shared generator code and edition config.
- [x] 2.3 Add neutral-entry browser-language detection for landing routes so English remains the default but French browsers redirect to `/fr/` unless the route is already explicit.
- [x] 2.4 Update site output assembly so `public/`, `public/fr/`, `public/assets/`, and `public/fr/assets/` are produced consistently without overwriting each other.

## 3. Add French mdBook generation and reader-shell localization

- [x] 3.1 Add the French mdBook config and source wiring so the English book continues at `/book/` and the French book builds at `/fr/book/`.
- [x] 3.2 Refactor reader post-build steps (`build:book-js`, `build:static-reader-sidebar`, `build:reader-meta`, and any new localization step) to run per edition and inject localized shell strings plus header-level language-switch metadata.
- [x] 3.3 Update `theme/index.hbs` and `theme/custom.js` integration points so localized toolbar labels, outline labels, search text, previous/next labels, and a visible book-header language switch can be injected without splitting the theme into two divergent directories.
- [x] 3.4 Add neutral-entry browser-language detection for the book entry route so English remains the default but French browsers redirect to `/fr/book/` unless the route is already explicit.

## 4. Make DOCX parity and figure validation edition-aware

- [x] 4.1 Replace English-only chapter marker assumptions in `scripts/docx_parity/*` with edition-driven chapter-title and anchor rules.
- [x] 4.2 Make `scripts/docx_figures/*`, `build_docx_figure_manifest.py`, and `check_docx_figures.py` consume edition-scoped summary paths, chapter roots, figure roots, manuscript aliases, and optional text-replacement maps.
- [x] 4.3 Add dedicated English and French parity/figure commands in `package.json`, including one top-level command that verifies both editions together.
- [x] 4.4 Replace the bootstrap French image tree with French-manuscript-derived published assets until `src-fr/images` no longer depends on English-origin figure binaries.

## 5. Extend verification and release gates

- [x] 5.1 Update `scripts/test-site-render.sh` and related source or render assertions so they verify both the English root output and the French `/fr/` output, including localized shell strings and language-switch links.
- [x] 5.2 Update any Python or shell tests that assume one edition so they accept edition config and validate locale-specific outputs.
- [x] 5.3 Promote the dual-edition build and validation flow into `.github/workflows/pages.yml` so Pages publishing fails if either edition fails.
