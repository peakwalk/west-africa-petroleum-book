## Context

The current repository is structurally single-edition:

- `src/` is the only content root for landing, legal, chapters, and book assets.
- `book.toml` declares one English mdBook build.
- landing-page generators and `scripts/shared/landing-shell.mjs` embed English copy and English-only routes.
- `theme/index.hbs` and `theme/custom.js` embed English reader labels and assume one edition.
- DOCX parity and figure inventory scripts hard-code English chapter markers such as `Chapter N:`.

The French manuscript inputs already exist in `resources/`, but they are not drop-in compatible with the current stack:

- the French DOCX does not expose English chapter titles, so the current parity extractor collapses it into front matter only;
- the French PDF filename uses Unicode accents, which is easy to mishandle in shell commands and package scripts;
- the current figure and manifest pipeline is single-root (`src/images/figure-manifest.json`) and partly English-specific;
- the current French source tree points `src-fr/images` at `src/images`, so French book pages consume the same published binaries as English even when the French manuscripts differ.

This is therefore a cross-cutting publishing change, not a copy-editing task.

## Goals / Non-Goals

**Goals:**
- Keep the English edition stable on the current routes.
- Add a French edition under `/fr/` and `/fr/book/`.
- Reuse one shared generator and validation stack across editions.
- Keep chapter slugs, figure numbers, and page families aligned across locales so language switching remains deterministic.
- Default neutral entry routes to English while automatically redirecting French-browser readers to the French edition.
- Make parity and figure validation edition-aware, including French chapter parsing and French manuscript aliases.

**Non-Goals:**
- Introduce full runtime browser i18n or page-by-page client-side content translation.
- Translate content on the fly from English sources.
- Merge English and French content into one mixed-language Markdown tree.
- Rebuild the site around a new framework or replace mdBook.

## Decisions

### 1. Use a shared edition registry plus parallel locale source roots

We will keep locale-specific content in parallel trees, with English remaining in `src/` and French added in `src-fr/`. A shared checked-in edition registry will declare each edition's:

- locale code
- public route prefix
- source root
- legal content root
- figure root and manifest path
- manuscript alias paths
- mdBook config path
- locale string catalog path

This is the cleanest MECE split:

- content differences live in locale roots;
- generator behavior lives in shared scripts;
- release wiring lives in top-level build/test commands.

Alternative considered:
- Introduce runtime i18n and keep one source tree. Rejected because chapters, legal text, figure captions, and PDF-backed assets are edition-specific content, not just UI strings.

### 2. Preserve identical internal slugs and figure numbering across editions

The French edition will use the same internal chapter filenames and figure numbers as the English edition even though page titles and chapter text are translated. This keeps:

- book page variant detection in `theme/custom.js`
- chapter-library derivation
- list-of-figures/list-of-tables references
- language switching between equivalent pages

simple and deterministic.

Alternative considered:
- Use translated French filenames and maintain a slug mapping table. Rejected because it would expand every generator, book post-build script, and language-switch rule into a two-way routing map with no user-facing benefit strong enough to justify the added complexity.

### 3. Add stable ASCII manuscript alias paths per edition

We will introduce canonical alias paths such as `resources/editions/en/reference.docx` and `resources/editions/fr/reference.docx` plus matching PDF aliases. Build and validation commands will target the aliases, not the original descriptive filenames.

This avoids:

- shell quoting drift
- Unicode normalization differences between composed and decomposed accented filenames
- duplicated literal resource paths across `package.json` and Python scripts

Alternative considered:
- Keep using the original resource filenames directly in every command. Rejected because the French PDF name is already a normalization hazard and the project is moving to multiple locale inputs.

### 4. Keep relative asset URLs stable by mirroring shared assets under each edition prefix

The current public pages and mdBook theme rely heavily on relative asset paths. For `/fr/book/...` pages, the existing relative pattern naturally resolves to `/fr/assets/...`. Instead of rewriting the whole asset-base model to root-relative URLs, we will copy shared assets into both:

- `public/assets`
- `public/fr/assets`

This preserves the current path model for both landing pages and book pages and minimizes risk in the theme.

Alternative considered:
- Rewrite the entire site to use root-relative asset URLs. Rejected because GitHub Pages deployments already depend on relative path behavior, and changing that across landing pages plus mdBook output would create more risk than duplicating static assets.

### 5. Localize reader-shell copy through a locale catalog plus post-build injection

The mdBook theme contains user-facing labels in `theme/index.hbs` and behavior-dependent strings in `theme/custom.js`. We will introduce one locale catalog per edition and make the book post-build pipeline inject locale-specific strings and runtime config into the built HTML/JS surface.

This avoids maintaining two divergent theme directories while still allowing:

- translated toolbar labels
- translated search placeholder and empty-state copy
- translated outline labels
- translated previous/next labels
- a visible landing-header language switch
- a visible book-header language switch

Alternative considered:
- Create separate `theme` and `theme-fr` directories. Rejected because most theme files are shared, and duplicated theme trees would drift quickly.

### 6. Use limited client-side locale negotiation only on neutral entry routes

Because GitHub Pages is static, the site cannot read `Accept-Language` on the server and cannot negotiate locale before sending HTML. The safe approach is:

- keep English content as the rendered default for neutral entry routes;
- run a tiny client-side check on neutral entry routes only;
- redirect to `/fr/` or `/fr/book/` when `navigator.languages` or `navigator.language` prefers French;
- never auto-redirect explicit edition routes such as `/fr/...`;
- let manual language-switch navigation establish an explicit route choice that takes precedence over browser preference.

This keeps the requirement narrow and predictable while avoiding full client-side i18n.

Alternative considered:
- Server-side locale negotiation. Rejected because the deployment target is static hosting.
- Auto-redirect every page based on browser language. Rejected because explicit route choice must win and chapter/legal deep links must remain stable.

### 7. Make Python validation config edition-aware through shared JSON inputs

Node build scripts and Python validation scripts both need access to the same edition metadata. The registry should therefore be stored in a format both runtimes can consume directly, with Python-specific regex and anchor metadata represented as data rather than hard-coded constants.

That metadata will include:

- chapter-title patterns
- front/back matter title patterns
- per-edition docx/pdf alias paths
- figure replacement map path, if any

Alternative considered:
- Keep one JS config and re-encode the same values by hand inside Python. Rejected because duplicated locale metadata would drift and break parity or figure validation silently.

### 8. Use a real French figure root, then replace bootstrap assets with French manuscript renders

The French edition needs two distinct phases:

- **isolation**: replace the `src-fr/images -> ../src/images` symlink with a real `src-fr/images/` directory so French builds and manifests can evolve independently;
- **content convergence**: re-render French published figures from the French DOCX/PDF inputs by figure kind until French web assets match French manuscript content and layout.

During isolation, it is acceptable to bootstrap `src-fr/images/` from the current published asset set so build paths remain stable. That bootstrap is not the release target. The release target is a fully French-manuscript-derived image tree.

This split is necessary because:

- build independence and content fidelity are separate problems;
- the French asset tree cannot be validated or incrementally repaired while it is still a symlink into the English root;
- some figures need PDF-backed rendering for layout fidelity, while others can come from DOCX-native extraction.

Alternative considered:
- Keep the French image root symlinked until every French figure is re-rendered. Rejected because it blocks edition-scoped manifests and hides whether French pages still depend on English binaries.

## Risks / Trade-offs

- [French source topology diverges from English slug topology] -> Enforce mirrored slugs and figure numbering in the French source tree and add render assertions for language-switch targets.
- [Post-build localization misses new reader strings] -> Centralize locale injection in one catalog and add render tests that assert French shell strings under `public/fr/book`.
- [Duplicated static assets increase publish size] -> Accept moderate duplication for path stability now; revisit deduplication only after both editions are stable.
- [DOCX extraction rules remain too English-centric] -> Move chapter and anchor rules into edition data and add fixture coverage for French chapter markers before wiring release gates.
- [Figure assets drift between editions] -> Keep locale-scoped figure roots and manifests, bootstrap a real French image directory early, and require French-manuscript re-renders plus edition-scoped figure validation before release.
- [Bootstrap copies are mistaken for final French assets] -> Treat copied assets only as an intermediate isolation step and keep an explicit remaining task to replace them with French-manuscript renders.

## Migration Plan

1. Introduce canonical manuscript aliases and an edition registry without changing public routes.
2. Add the French source tree with mirrored slugs, legal content, and placeholder/localized landing content.
3. Refactor landing/legal/chapters generators and shared shell links to read edition data and write `/fr/*` output.
4. Add a French mdBook config and extend post-build reader scripts so `/fr/book` localizes correctly and exposes a header-level language switch.
5. Make parity and figure validation edition-aware, bootstrap the French image root, and add dedicated French commands.
6. Re-render French published figures from the French manuscripts until the French asset tree no longer depends on English-derived binaries.
7. Promote top-level build/test/Pages workflows to require both editions.

Rollback strategy:

- disable the French edition entry in the edition registry and top-level build orchestration;
- keep the English root build intact because its routes and content roots remain unchanged.

## Open Questions

- None for planning. The change assumes French and English chapter slugs remain aligned and that the French edition is published as a sibling route family under `/fr/`.
