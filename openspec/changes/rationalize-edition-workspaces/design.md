## Context

The current multilingual topology is functional but structurally inconsistent:

- English content, mdBook config, and generated landing/legal/chapter pages live at the repository root.
- French content is split across `src-fr/`, `books/fr/`, `fr/`, and `public/fr/`.
- The edition registry in `config/editions.json` enumerates many derived paths (`bookRoot`, `sourceRoot`, `summaryPath`, `chapterRoot`, `legalRoot`, `figureRoot`, `figureManifestPath`, `localeCatalog`) instead of declaring one locale root and deriving the rest.
- Root-level static HTML (`index.html`, `chapters/index.html`, legal pages, `fr/*.html`) is committed even though the build ultimately republishes into `public/`.

That structure mixes two dimensions:

1. locale ownership: which files belong to one language edition;
2. build stage: source inputs versus generated publish output.

This change is a cross-cutting repo refactor. It affects Node generators, mdBook entry points, Python validation scripts, preview flows, and test expectations. The published route contract from the French edition change remains in force: English stays on the root routes, French stays under `/fr/`.

## Goals / Non-Goals

**Goals:**
- Make every locale use the same internal workspace shape.
- Preserve the current public routes and language-switch behavior.
- Reduce edition configuration to one root per locale plus route prefix and manuscript aliases.
- Make `public/` the only generated publish artifact directory.
- Remove committed generated landing/legal/chapter HTML outside `public/`.
- Keep locale-specific figure manifests and validation inputs aligned with the new workspace roots.

**Non-Goals:**
- Change any public URL from `/`, `/book/`, `/fr/`, or `/fr/book/`.
- Replace mdBook or the current shared theme model.
- Merge English and French content into a single multilingual Markdown tree.
- Rework figure-rendering algorithms beyond path and ownership updates required by the new layout.
- Introduce runtime i18n or client-side template rendering for the public site.

## Decisions

### 1. Introduce a single edition workspace root per locale

Each locale will move under `editions/<locale>/` with a fixed internal shape:

```text
editions/
  en/
    book.toml
    locale.json
    site/
      index-main.html
      legal/
    source/
      images/
    content/
      SUMMARY.md
      chapters/
      images/
        figure-manifest.json
  fr/
    book.toml
    locale.json
    site/
      index-main.html
      legal/
    source/
      images/
    content/
      SUMMARY.md
      chapters/
      images/
        figure-manifest.json
```

This gives every edition one discoverable ownership boundary. Any file that differs by locale lives below that edition root. Shared assets, theme files, scripts, and manuscript aliases remain top-level shared resources.
Retained raw or backup images that are not part of the published book should live under `source/images/`, while published book assets and `figure-manifest.json` remain under `content/images/`.

Alternative considered:
- Keep the current `src/` and `src-fr/` split while only adding `books/en` and `site/en`. Rejected because it preserves multiple path conventions for locale-owned inputs and leaves root-level English as a structural exception.

### 2. Reduce edition registry entries to `editionRoot` plus route data

`config/editions.json` will declare:

- `locale`
- `editionRoot`
- `routePrefix`
- manuscript alias paths
- optional figure text replacement map

All other paths become derived conventions:

- `bookConfigPath = <editionRoot>/book.toml`
- `localeCatalogPath = <editionRoot>/locale.json`
- `siteRoot = <editionRoot>/site`
- `landingMainPath = <editionRoot>/site/index-main.html`
- `legalRoot = <editionRoot>/site/legal`
- `contentRoot = <editionRoot>/content`
- `summaryPath = <editionRoot>/content/SUMMARY.md`
- `chapterRoot = <editionRoot>/content/chapters`
- `figureRoot = <editionRoot>/content/images`
- `figureManifestPath = <editionRoot>/content/images/figure-manifest.json`

This keeps Node and Python loaders aligned and removes a large class of registry drift bugs.

Alternative considered:
- Keep explicit per-path registry fields and only move files around. Rejected because the duplicated path catalog is itself part of the maintenance burden.

### 3. Treat `public/` as the only publish output and stop versioning static HTML elsewhere

Landing, legal, and chapter-library generators will write directly to `public/` instead of creating committed root HTML and then copying it again during `build:site`. After migration:

- `public/index.html`, `public/chapters/index.html`, and root legal pages come directly from generators.
- `public/fr/index.html`, `public/fr/chapters/index.html`, and French legal pages come directly from generators.
- `public/book/` and `public/fr/book/` come directly from mdBook plus post-build reader scripts.

The repo root and `fr/` will no longer contain generated publish pages.

Alternative considered:
- Keep committed root and `fr/` pages for easier manual inspection. Rejected because it duplicates publish-state artifacts, confuses source ownership, and forces tests to manage backups/restores of generated files.

### 4. Keep route-prefix semantics independent from workspace layout

The internal edition workspace becomes symmetric, but route behavior stays asymmetric by design:

- English `routePrefix = ""`
- French `routePrefix = "fr"`

This preserves historical links and the existing edition spec while allowing internals to become fully regular.

Alternative considered:
- Introduce `/en/` and `/en/book/` to match `/fr/`. Rejected because it would be a user-visible route migration with unnecessary SEO and compatibility cost for a structural refactor.

### 5. Convert root-level `build` workflows to call the site assembler, not legacy single-edition paths

`package.json` currently keeps legacy commands that generate root pages and a root `book/` directory. The stable workflow after migration should be:

- `npm run build:site` is the canonical build.
- `npm run build` becomes an alias to `npm run build:site`.
- Preview and verification scripts should assume `public/` as the assembled artifact root.

This avoids having two incompatible build entry points that generate different directory shapes.

Alternative considered:
- Preserve both legacy and new build flows indefinitely. Rejected because dual workflows will keep reintroducing old path assumptions into tests and contributor habits.

### 6. Use a phased migration with temporary compatibility, then delete legacy roots

The migration will intentionally separate:

1. creating `editions/` and moving data;
2. switching loaders and generators;
3. deleting legacy roots and committed generated pages.

This keeps rollback simple until the final cleanup pass.

Alternative considered:
- Move all files and switch all scripts in one commit. Rejected because it creates a high-risk failure domain across mdBook path resolution, figure validation, and render tests.

## Risks / Trade-offs

- [mdBook relative theme or asset paths break after moving `book.toml`] → Update both edition `book.toml` files and add build assertions for `public/book/index.html` and `public/fr/book/index.html`.
- [Tests still depend on committed root HTML or `fr/` content] → Migrate render tests to assert against `public/` or temporary output roots before deleting legacy generated pages.
- [Python and Node loaders diverge on derived path rules] → Keep the `editionRoot` derivation contract explicit in both `scripts/shared/site-editions.mjs` and `scripts/edition_config.py`, and add registry shape tests.
- [Figure manifests or replacement maps break during content relocation] → Move manifests with edition content roots and keep explicit tests for figure root ownership and manifest paths.
- [Contributors continue editing legacy directories during the compatibility window] → Document the new edition roots in repo guidance and delete legacy compatibility layers as soon as the new pipeline is stable.
- [Removing committed static pages makes ad hoc review less convenient] → Use `npm run build:site` and `scripts/preview.sh` as the only inspection path; accept this trade-off to regain source/output clarity.

## Migration Plan

1. Create `editions/en/` and `editions/fr/` with the target directory shape, and copy locale-owned inputs into those roots without deleting legacy paths yet.
2. Refactor `config/editions.json`, `scripts/shared/site-editions.mjs`, and `scripts/edition_config.py` to use `editionRoot` and derived subpaths.
3. Move mdBook configs to `editions/en/book.toml` and `editions/fr/book.toml`, then update `build_site.mjs` to build from those paths into `public/book` and `public/fr/book`.
4. Move landing/legal/chapter source inputs into `editions/*/site/` and update the generators to read from those locations.
5. Add generator output-root support and change the site assembler so generators write directly into `public/` rather than writing committed root pages first.
6. Update render tests, preview scripts, and package scripts to treat `public/` as the only publish output.
7. Delete legacy generated static HTML (`index.html`, `chapters/index.html`, root legal pages, `fr/`) after all tests pass on the direct-to-`public/` flow.
8. Delete leftover legacy source paths and compatibility layers (`src/`, `src-fr/`, `books/fr/`, root `book.toml`, old locale catalog locations) once the new edition roots are the sole source of truth.

Rollback strategy:

- Before step 7, rollback means reverting registry and script changes while legacy roots still exist.
- After step 7, rollback means restoring the deleted generated-page layer from Git and reverting the direct-to-`public/` generator changes.
- Do not delete legacy source directories until the new build, parity, and figure checks all pass together.

## Open Questions

- None for planning. The target structure, route-preservation contract, and `public/`-only output model are intentionally fixed by this change.
