## Why

The repo currently publishes one English landing page and one English mdBook from a single set of hard-coded source paths, labels, and validation commands. The French DOCX and PDF source files already exist under `resources/`, but the current pipeline cannot ingest, validate, build, and publish a French edition without either breaking the English edition or duplicating the whole generator stack. In addition, the current French source tree reuses the shared English image root, so French web figures can drift from the French DOCX/PDF in both text and layout.

## What Changes

- Introduce an edition-aware publishing model that keeps the English edition at the current root routes and adds a French edition under `/fr/` and `/fr/book/`.
- Add a visible language-switch control to the landing-page header and the book-reader header so readers can move between English and French from the primary navigation surface.
- Add edition-neutral entry behavior that defaults to English but automatically redirects to the French edition when the browser language preference is French.
- Add a single edition registry that defines per-edition source roots, manuscript aliases, output prefixes, book config, figure assets, locale strings, and validation inputs.
- Refactor landing, legal, chapters, and book post-build scripts so they can render either edition from shared generator code instead of hard-coded English paths and copy.
- Add a French source tree, French legal content, French landing copy, and French figure/manuscript assets with the same chapter/file slug topology as the English edition.
- Replace the French image-root symlink with a real locale-owned figure root so French builds, manifests, and validations no longer depend on the English shared image directory.
- Extend the DOCX parity and figure-validation pipeline so it can parse French chapter markers and validate figures against the French manuscript and PDF inputs.
- Re-render French published figures from the French DOCX/PDF inputs until the French web edition no longer relies on English-derived figure binaries as placeholders.
- Update build, test, and Pages publishing commands so both editions are generated and verified together.

## Capabilities

### New Capabilities
- `localized-site-editions`: Publish independent English and French public routes with localized landing, legal, chapter-library, and reader entry points.
- `localized-book-sources`: Resolve edition-specific Markdown, legal content, figure assets, and manuscript inputs from one shared edition registry.
- `localized-parity-validation`: Validate each edition against its own DOCX/PDF source set, including French chapter parsing and figure checks.

### Modified Capabilities
- None.

## Impact

- Affected source files will include `package.json`, `book.toml`/`book.fr.toml`, `theme/index.hbs`, `theme/custom.js`, `scripts/generate-*.mjs`, `scripts/build_*`, `scripts/check_docx_*`, and `scripts/docx_figures/*`.
- New edition content and assets will be added under a French source root plus locale-specific manuscript alias paths.
- Build output under `public/` will expand to include `/fr`, `/fr/assets`, `/fr/chapters`, and `/fr/book`.
- GitHub Pages build and local site verification will change from single-edition generation to dual-edition generation.
