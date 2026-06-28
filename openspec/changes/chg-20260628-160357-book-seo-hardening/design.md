## Context

The current site build pipeline already treats the book output as a post-processed artifact, not a pure mdBook export. `scripts/build_site.mjs` builds each edition, then runs repo-owned post-build steps such as `build_reader_page_meta.mjs`, `build_static_reader_sidebar.mjs`, and `localize_reader_shell.mjs`.

That architecture is the right place to add SEO hardening because the generated HTML now contains facts that mdBook templates alone do not have: bilingual route prefixes, chapter-to-chapter equivalence, extracted ledes, and root-level output paths. A fresh local build confirms the current gap: `/book/` and `/fr/book/` emit empty `meta name="description"` values, no canonical links, no JSON-LD, and no root `robots.txt` or `book-sitemap.xml`.

There is also a correctness constraint around locale mapping. `scripts/localize_reader_shell.mjs` currently uses one `CROSS_LOCALE_PAGE_MAP` that intentionally falls back some English-only pages to `/fr/book/` for UI navigation. That fallback is acceptable for a reader switcher, but it is not acceptable for SEO alternates because `hreflang` must only connect equivalent pages.

## Goals / Non-Goals

**Goals:**
- Publish stable SEO metadata for canonical book landing, chapter, and reference pages in both editions.
- Keep `/book/` and `/fr/book/` stable as cover pages so the canonical book root and the reader `Cover` navigation target stay aligned.
- Generate a dedicated `book-sitemap.xml` and reference it from a root `robots.txt`.
- Ensure `hreflang` output only advertises true EN/FR equivalents; non-equivalent English-only pages keep self-reference plus `x-default`.
- Reuse existing build-time metadata extraction where possible and keep crawlable chapter bodies in static HTML.

**Non-Goals:**
- Change chapter body copy, translation scope, or canonical route paths beyond removing the client-side auto-forward from the book home route.
- Automate Google Search Console submission.
- Rework the public marketing landing pages outside the `/book/` and `/fr/book/` surfaces.
- Replace mdBook or move SEO concerns into a new external service.

## Decisions

### Decision: Implement SEO as a repo-owned post-build injector
The SEO change spans generated book HTML, canonical absolute URLs, bilingual equivalence, JSON-LD, and root-level sitemap/robots assets. A post-build script can work on the final `public/book/**` and `public/fr/book/**` trees, which already incorporate mdBook output plus the repo’s reader shell customizations.

Alternative considered:
- Push all SEO logic into `theme/index.hbs`. Rejected because the template does not naturally own absolute site origin, curated locale equivalence, root sitemap generation, or per-page extracted descriptions across both editions.

### Decision: Use edition-local SEO override data with automatic lede fallback
Most numbered chapters already have a good first paragraph that can seed a unique description. Special pages such as the landing cover, disclaimer, figure/table/equation indexes, glossary, and bibliographical references need curated copy because their first block is often too short, too repetitive, or not SEO-friendly.

The design will therefore keep curated SEO overrides in edition-local JSON files and fill the rest from the existing `build_reader_page_meta.mjs` lede extraction. This keeps manual copy scoped to the pages that actually need it.

Alternative considered:
- Hardcode all metadata in the injector script. Rejected because it would hide editorial copy inside implementation logic and make future metadata refreshes harder.
- Require hand-authored descriptions for every page. Rejected because it adds too much maintenance noise for standard chapters that already have usable source text.

### Decision: Split cross-locale navigation mapping from SEO equivalence mapping
The current navigation mapping intentionally degrades to locale home pages when no translation-equivalent page exists. For SEO we need a stricter contract: reciprocal `hreflang` only for actual equivalents, self-reference plus `x-default` otherwise.

The implementation will move the mapping data into a shared module with two exported views:
- navigation mapping for reader UI
- SEO equivalence mapping for canonical alternates and structured-data peer links

Alternative considered:
- Reuse the current UI map for `hreflang`. Rejected because it would publish non-equivalent alternates, which is exactly what the user asked us not to do.

### Decision: Keep book root on the cover page and move reading progression behind explicit CTA
The `/book/` and `/fr/book/` routes are now canonical landing pages with `Book` schema, sidebar `Cover` states, and canonical URL responsibilities. They should therefore remain stable cover pages instead of immediately forwarding to the default reading chapter. The `Start reading` and `Commencer la lecture` cover CTAs already provide an explicit way to enter the chapter flow without making the book root itself unstable.

Alternative considered:
- Keep the auto-forward and special-case the `Cover` sidebar row. Rejected because it would preserve the same user-facing mismatch: the `Cover` destination would still resolve through a route whose primary behavior is to leave the cover.

### Decision: Generate discovery artifacts from the final canonical page inventory
`book-sitemap.xml` and `robots.txt` should reflect the exact pages that are publishable after all build steps have run. The generator will walk the final public book outputs, exclude redirect-only pages such as `chapters/front-matter.html`, and emit absolute URLs under `https://upstreamatlas.com`.

This design intentionally does not trust the current mdBook `site-url` values as SEO truth. The English `book.toml` still points to a historical path (`/west-africa-petroleum-book/book/`), so canonical URL generation must be driven by repo-owned site-origin configuration instead.

Alternative considered:
- Build sitemap entries from source markdown or `SUMMARY.md` directly. Rejected because it would miss post-build route normalization and redirect exclusions.

### Decision: Emit structured data by page class, not one schema for every page
Landing pages will emit `Book` JSON-LD. Numbered chapter pages will emit `Chapter` plus `BreadcrumbList`. Reference pages such as glossary, bibliography, and auxiliary indexes will emit `WebPage` plus `BreadcrumbList` so the markup stays truthful to the page surface.

Alternative considered:
- Emit `Article` for every `/chapters/*.html` page. Rejected because front matter and reference indexes are not articles, and forcing one schema everywhere would make the markup noisier and less accurate.

## Risks / Trade-offs

- [SEO override files can drift from page inventory] → Keep override files edition-local, use automatic lede fallback for standard chapters, and add tests that fail on empty or duplicate metadata.
- [Locale equivalence changes may break `hreflang`] → Centralize the SEO equivalence map in one shared module and cover representative equivalent and non-equivalent pages in tests.
- [Post-build HTML rewriting could damage reader output] → Restrict rewriting to the `<head>` plus additive discovery artifacts, and add regression checks that representative chapter body text remains in static markup.
- [Book titles disagree across current sources] → Use curated SEO overrides for landing/cover metadata instead of blindly trusting the current mdBook title string.

## Migration Plan

1. Add the OpenSpec artifacts and failing metadata/sitemap tests first.
2. Introduce shared SEO helpers and edition-local override data.
3. Implement the post-build SEO injector for `public/book/**` and `public/fr/book/**`.
4. Implement sitemap/robots generation from the final page inventory and wire both steps into `scripts/build_site.mjs`.
5. Rebuild the site, run the targeted Python/site checks, and inspect representative English/French outputs.
6. If rollback is needed, remove the SEO injector and sitemap/robots step from the build, restore the prior mapping arrangement, and rebuild the site.

## Open Questions

- None for this change. The only policy decision about untranslated English pages was resolved by the user: keep self-reference plus `x-default`, and do not emit a non-equivalent French alternate.
