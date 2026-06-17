## 1. Create the symmetric edition workspaces

- [x] 1.1 Create `editions/en/` and `editions/fr/` with the target `book.toml`, `locale.json`, `site/`, and `content/` layout while keeping legacy paths intact during the transition.
- [x] 1.2 Copy English and French locale-owned inputs into the new edition roots, including landing source content, legal source content, Markdown chapters, figure assets, and figure manifests.
- [x] 1.3 Add or update structural tests that assert both edition roots expose the same required workspace shape and that the French figure root remains a real directory.

## 2. Refactor the edition registry and path loaders

- [x] 2.1 Simplify `config/editions.json` so each locale is declared by `editionRoot`, `routePrefix`, manuscript aliases, and any optional figure text replacement map.
- [x] 2.2 Update `scripts/shared/site-editions.mjs` to derive book, site, content, legal, locale-catalog, chapter, figure-root, and figure-manifest paths from `editionRoot`.
- [x] 2.3 Update `scripts/edition_config.py` and any dependent Python validation helpers to resolve the same derived path contract as the Node loader.
- [x] 2.4 Update registry-focused tests so Node and Python path resolution stay aligned.

## 3. Migrate generators and mdBook entry points

- [x] 3.1 Move the English and French mdBook configs into `editions/en/book.toml` and `editions/fr/book.toml`, then update the site assembler to build them into `public/book` and `public/fr/book`.
- [x] 3.2 Move landing, legal, and chapter-library source inputs into `editions/*/site/` and update the generators to read from those edition-local paths.
- [x] 3.3 Add output-root support to the landing, legal, and chapter-library generators so they can write directly into `public/` by route prefix.
- [x] 3.4 Update `package.json` build and preview entry points so `build:site` becomes the canonical assembled-site workflow.

## 4. Shift verification to public-only publish artifacts

- [x] 4.1 Update `tests/test_public_editions.py` to validate generated landing/legal/chapter outputs from `public/` or controlled temporary output roots rather than committed root HTML.
- [x] 4.2 Update `tests/test_book_editions.py`, `scripts/test-site-render.sh`, and preview-related checks to treat `public/` as the only publish artifact tree.
- [x] 4.3 Run the narrowest relevant project checks for the new topology, including `npm run build:site`, `npm run test:site`, `npm run check:docx-parity:all`, and `npm run check:docx-figures:all`, then fix any path regressions.

## 5. Remove legacy topology and compatibility layers

- [x] 5.1 Delete committed generated landing/legal/chapter HTML outside `public/`, including root static pages and the root-level `fr/` tree, after the direct-to-`public/` flow is verified.
- [x] 5.2 Delete legacy locale-owned source roots and wiring that are no longer needed, including `src/`, `src-fr/`, `books/fr/`, the root `book.toml`, and old locale-catalog paths.
- [x] 5.3 Sweep repository scripts, tests, and contributor-facing docs for old path references so `editions/<locale>/` and `public/` become the only documented source/output model.
