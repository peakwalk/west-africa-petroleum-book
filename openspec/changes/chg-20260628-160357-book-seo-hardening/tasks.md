## 1. OpenSpec and failing SEO coverage

- [x] 1.1 Add the proposal, design, and `book-seo-indexability` capability spec for bilingual book SEO hardening.
- [x] 1.2 Add failing tests for sitemap/robots generation, absolute canonical metadata, reciprocal-vs-self-only `hreflang`, structured data, and static chapter-body preservation on representative English and French book pages.

## 2. Book SEO metadata pipeline

- [x] 2.1 Add shared SEO helpers/config for site origin, canonical URL building, and separate navigation-versus-SEO locale mappings.
- [x] 2.2 Implement a post-build SEO injector for landing, chapter, and reference pages that emits unique title/description/canonical data, `hreflang`, `x-default`, and page-type-specific JSON-LD.

## 3. Discovery artifacts and build wiring

- [x] 3.1 Generate `book-sitemap.xml` and root `robots.txt` from the final canonical bilingual book page inventory, excluding redirect shims.
- [x] 3.2 Wire the SEO injector and discovery-artifact generation into `scripts/build_site.mjs` after the existing reader metadata and localization steps.

## 4. Verification and regression tightening

- [x] 4.1 Update site-render assertions and metadata-focused tests so empty or duplicate book SEO output fails fast in both editions.
- [x] 4.2 Run the narrowest relevant build/test commands and inspect representative generated English/French pages for the expected SEO head markup and sitemap output.
- [x] 4.3 Keep `/book/` and `/fr/book/` on the cover page by removing the default-chapter auto-forward, while preserving explicit reading CTAs and locale-preference redirects.
