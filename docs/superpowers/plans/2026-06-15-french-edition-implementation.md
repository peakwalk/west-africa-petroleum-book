# French Edition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a French landing page and French mdBook edition that publish beside the current English edition, expose language switching in the landing header and book header, default neutral entry routes to English, redirect French-browser readers to French entry routes, and validate against the French DOCX/PDF manuscript inputs.

**Architecture:** Keep locale-specific content in parallel source roots, but make all build, reader post-processing, parity, and figure scripts edition-aware through one shared edition registry. Preserve English root routes, publish French under `/fr`, and keep chapter slugs and figure numbering aligned across locales.

**Tech Stack:** Node.js build scripts, mdBook, Handlebars theme templates, Python parity/figure scripts, shell render assertions, OpenSpec planning artifacts

---

## Source of Truth

This file is an execution plan, not the canonical design record.

Authoritative planning artifacts for this change:

- OpenSpec proposal: `openspec/changes/add-french-edition/proposal.md`
- OpenSpec specs:
  - `openspec/changes/add-french-edition/specs/localized-site-editions/spec.md`
  - `openspec/changes/add-french-edition/specs/localized-book-sources/spec.md`
  - `openspec/changes/add-french-edition/specs/localized-parity-validation/spec.md`
- OpenSpec design: `openspec/changes/add-french-edition/design.md`
- OpenSpec tasks: `openspec/changes/add-french-edition/tasks.md`

If this plan ever conflicts with the OpenSpec change artifacts, follow the OpenSpec files and update this plan instead of treating this file as a second design source.

---

## Solution Summary

### File Map

- Create: `src-fr/`
  French landing, legal, chapters, images, and summary content root.
- Create: `book.fr.toml`
  French mdBook config.
- Create: `resources/editions/en/reference.docx`
- Create: `resources/editions/en/reference.pdf`
- Create: `resources/editions/fr/reference.docx`
- Create: `resources/editions/fr/reference.pdf`
  Stable manuscript aliases for build and validation commands.
- Create: shared edition registry and locale catalogs
  One data source for routes, labels, source paths, manuscript aliases, and validation rules.
- Modify: `scripts/generate-index-page.mjs`
- Modify: `scripts/generate-legal-pages.mjs`
- Modify: `scripts/generate-chapters-page.mjs`
- Modify: `scripts/shared/landing-shell.mjs`
  Public-page generation becomes edition-aware, adds a visible landing-header language switch, and supports neutral-entry language redirects.
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/build_reader_page_meta.mjs`
- Modify: `scripts/build_static_reader_sidebar.mjs`
  Reader shell becomes locale-aware, adds a visible book-header language switch, and supports neutral-entry book redirects.
- Modify: `scripts/check_docx_parity.py`
- Modify: `scripts/check_docx_figures.py`
- Modify: `scripts/docx_parity/*`
- Modify: `scripts/docx_figures/*`
  Validation becomes edition-aware.
- Replace: `src-fr/images` symlink with a real locale-owned directory
  French figure assets can be validated and re-rendered independently of `src/images`.
- Modify: `package.json`
- Modify: `scripts/test-site-render.sh`
- Modify: `.github/workflows/pages.yml`
  Dual-edition orchestration and release gating.

### Rollout Order

1. Stabilize inputs and config.
2. Add French content tree.
3. Refactor public-page generation.
4. Add French mdBook build and reader localization.
5. Refactor validation and figure scripts.
6. Promote dual-edition verification into release gates.

---

### Task 1: Stabilize edition inputs and shared configuration

**Files:**
- Create: canonical manuscript aliases under `resources/editions/`
- Create: shared edition registry and locale catalogs
- Modify: `package.json`

- [ ] **Step 1: Add canonical manuscript aliases**
Document and create stable alias targets for both English and French DOCX/PDF inputs so all future commands stop referencing the descriptive original filenames directly.

- [ ] **Step 2: Add the shared edition registry**
Define per-edition data for locale code, route prefix, source root, legal root, figure root, manifest path, book config path, and validation metadata.

- [ ] **Step 3: Add edition-aware npm entrypoints**
Replace hard-coded manuscript and source-root assumptions in `package.json` with edition-aware build and validation commands, plus a top-level command that runs both editions.

- [ ] **Step 4: Verify config readability**
Run the narrowest script or smoke command that loads the registry in both Node and Python contexts and confirm both editions resolve expected paths.

### Task 2: Add the French source tree with mirrored topology

**Files:**
- Create: `src-fr/SUMMARY.md`
- Create: `src-fr/index-main.html`
- Create: `src-fr/legal/*.json`
- Create: `src-fr/chapters/*.md`
- Create: `src-fr/images/*`
- Create: `book.fr.toml`

- [ ] **Step 1: Mirror the English topology**
Create the French source root with the same internal chapter filenames, legal page keys, and figure numbering as English.

- [ ] **Step 2: Add French landing and legal content**
Translate or stage the French landing and legal copy while keeping the same structural slots expected by the current generators.

- [ ] **Step 3: Add French chapter and figure sources**
Place French chapter Markdown, summary wiring, figure assets, and figure manifest targets under `src-fr/` without changing English source paths.

- [ ] **Step 4: Verify slug parity**
Run a path-level comparison between `src/chapters` and `src-fr/chapters` to confirm the slug set matches exactly.

### Task 3: Refactor public-page generation and shell links

**Files:**
- Modify: `scripts/shared/landing-shell.mjs`
- Modify: `scripts/generate-index-page.mjs`
- Modify: `scripts/generate-legal-pages.mjs`
- Modify: `scripts/generate-chapters-page.mjs`

- [ ] **Step 1: Make shell links, labels, and the landing-header switch edition-aware**
Move public-facing labels, route construction, and the header-level language-switch target into edition-aware data so the shared shell can render English and French correctly.

- [ ] **Step 2: Make page generators edition-aware**
Refactor landing, legal, and chapter-library generators to accept an edition context and write output into the correct route family.

- [ ] **Step 3: Add neutral landing-route browser-language detection**
Implement entry-route logic that leaves English as the default landing output but redirects French-browser readers to `/fr/` when the route is edition-neutral.

- [ ] **Step 4: Assemble per-edition assets**
Update site assembly so shared static assets are copied into both `public/assets` and `public/fr/assets`.

- [ ] **Step 5: Verify generated public routes**
Run the site build and confirm English root pages plus French `/fr/` pages all exist with locale-correct labels, links, landing-header language-switch targets, and neutral-entry redirect behavior.

### Task 4: Add French mdBook build and reader-shell localization

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/build_reader_page_meta.mjs`
- Modify: `scripts/build_static_reader_sidebar.mjs`
- Modify: build orchestration around `mdbook build`
- Create: any locale injection helper needed by the reader pipeline

- [ ] **Step 1: Add the French book config and build target**
Wire `book.fr.toml` into the build so French content can publish under `/fr/book` while English remains under `/book`.

- [ ] **Step 2: Inject localized reader strings and book-header switch targets**
Add locale-aware labels for toolbar, search, outline, previous/next navigation, and the visible book-header language switch without duplicating the whole theme.

- [ ] **Step 3: Keep chapter mapping deterministic**
Use mirrored slugs so reader meta, page variants, and language switching work for both editions without a separate routing table.

- [ ] **Step 4: Add neutral book-route browser-language detection**
Implement entry-route logic that leaves English as the default book output but redirects French-browser readers to `/fr/book/` when the route is edition-neutral.

- [ ] **Step 5: Verify localized reader output**
Inspect generated `/book` and `/fr/book` output for expected English and French shell strings, a working book-header language switch, and neutral-entry redirect behavior.

### Task 5: Refactor parity and figure validation for edition awareness

**Files:**
- Modify: `scripts/check_docx_parity.py`
- Modify: `scripts/check_docx_figures.py`
- Modify: `scripts/docx_parity/*`
- Modify: `scripts/docx_figures/*`

- [ ] **Step 1: Externalize chapter and anchor rules**
Replace English-only parsing constants with edition-driven data so French chapter extraction can identify all expected sections.

- [ ] **Step 2: Scope figure inventory by edition**
Make figure manifest generation and figure validation read the targeted edition's summary, chapter root, figure root, manuscript aliases, and replacement-map settings.

- [ ] **Step 3: Replace the French image-root symlink with a real directory**
Bootstrap `src-fr/images` as a real locale-owned root so French manifests and renderers stop depending on the shared English image tree.

- [ ] **Step 4: Re-render French published figures from French manuscripts**
Replace bootstrap French assets by figure kind until French web figures align with French DOCX/PDF content and layout.

- [ ] **Step 5: Add per-edition verification commands**
Expose dedicated English and French parity/figure commands plus a combined verification command.

- [ ] **Step 6: Verify failure surfaces**
Run the French parity and figure commands on the French manuscript paths and confirm failures, if any, reference French chapter or figure locations rather than English ones.

### Task 6: Promote dual-edition verification into site and release gates

**Files:**
- Modify: `scripts/test-site-render.sh`
- Modify: `.github/workflows/pages.yml`
- Modify: any related shell or Python tests that assume a single edition

- [ ] **Step 1: Extend render assertions**
Add source and output assertions for `/fr`, `/fr/book`, localized labels, and language-switch links.

- [ ] **Step 2: Make top-level site verification dual-edition**
Ensure the site test command fails if either edition fails build, parity, figure, or render checks.

- [ ] **Step 3: Promote the same contract to Pages**
Update GitHub Pages publishing so it runs the dual-edition verification path before upload.

- [ ] **Step 4: Final verification**
Run the narrowest complete verification set for this change: the dual-edition site build, dual-edition parity checks, dual-edition figure checks, and dual-edition render assertions.
