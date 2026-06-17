## Why

The repo's multilingual layout currently mixes locale ownership with build-stage ownership. English source and generated files live at the repository root, while French equivalents are split across `src-fr/`, `books/fr/`, `fr/`, and `public/fr/`. That asymmetry makes routine edits error-prone, obscures which directories are source versus generated output, and makes future locale additions unnecessarily expensive.

The French edition launch solved route and content requirements, but it preserved root-level English special cases and committed static pages outside `public/`. The next change should normalize the repo into one edition-oriented source model before more locales, assets, and tests accumulate on top of the current layout.

## What Changes

- Introduce a single `editions/<locale>/` workspace shape for locale-owned book config, landing/legal source content, Markdown content, figure assets, and locale catalogs.
- Move English and French edition inputs into symmetric `editions/en/` and `editions/fr/` roots while preserving the current public routes: English remains `/` and `/book/`; French remains `/fr/` and `/fr/book/`.
- Refactor shared edition configuration so build and validation scripts derive per-locale paths from `editionRoot` instead of enumerating separate `sourceRoot`, `legalRoot`, `bookRoot`, and locale catalog paths.
- Change landing, legal, and chapter-library generators so they write directly to `public/` rather than generating committed HTML under the repo root and `fr/`.
- Remove committed static landing/legal/chapter outputs from the repo root and `fr/` once the direct-to-`public/` pipeline is stable.
- Retire compatibility layers that only exist to bridge the old topology, including `books/fr` symlink wiring and the root-level English `book.toml` special case.
- Keep shared assets, theme files, validation scripts, and manuscript aliases outside the edition workspaces unless they are locale-specific.

## Capabilities

### New Capabilities
- `edition-workspace-layout`: Locale-owned site, book, and figure inputs are organized under one symmetric edition workspace per locale.
- `edition-static-output-pipeline`: Shared generators and mdBook builds publish both editions directly into `public/` without committed static HTML outside the publish directory.

### Modified Capabilities
- None.

## Impact

- Affected code will include `config/editions.json`, `scripts/shared/site-editions.mjs`, `scripts/edition_config.py`, `scripts/build_site.mjs`, `scripts/generate-*.mjs`, `package.json`, preview scripts, and site-render tests.
- Locale-owned source files will move from `src/`, `src-fr/`, `book.toml`, `books/fr/`, `config/locales/`, and root-level generated HTML into `editions/en/` and `editions/fr/`.
- Build verification will shift from checking a mix of committed root pages and generated `public/` output to treating `public/` as the only publish artifact.
- No public route changes are introduced; the change is internal topology and build-pipeline restructuring with compatibility preserved at the URL layer.
