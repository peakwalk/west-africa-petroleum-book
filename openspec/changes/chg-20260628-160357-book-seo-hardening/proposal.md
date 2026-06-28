## Why

The bilingual book output is already crawlable HTML, but the generated `/book/` and `/fr/book/` pages still ship with empty book-page descriptions, no absolute canonical URLs, no structured data, and no dedicated sitemap or `robots.txt` entry for the book surface. The current cross-locale page mapping is also tuned for reader navigation, not SEO equivalence, so it can point untranslated English pages at the French home page instead of withholding a non-equivalent `hreflang`. The current reader shell also auto-forwards `/book/` to the default reading chapter, which means the sidebar `Cover` entry does not actually land on the cover page.

UA-10 requires the book to be indexable as a first-class search surface, starting with the English edition and preserving the bilingual reader shell. We need a repo-owned SEO hardening pass now so Search Console submission and future rebuilds use stable discovery artifacts and page-level metadata instead of one-off manual fixes.

## What Changes

- Add a post-build SEO hardening step for the generated bilingual book output so `/book/`, `/fr/book/`, and canonical chapter/reference pages receive unique titles, non-empty descriptions, absolute canonical URLs, `hreflang` tags, `x-default`, and structured data.
- Keep `/book/` and `/fr/book/` as stable cover destinations and reserve chapter progression for explicit cover CTAs such as `Start reading` / `Commencer la lecture`.
- Generate a root `book-sitemap.xml` covering canonical English and French book URLs, plus a root `robots.txt` that references that sitemap.
- Separate reader language-navigation fallbacks from SEO alternate-page equivalence so only real EN/FR counterparts receive reciprocal `hreflang` links; untranslated English-only pages will keep self-reference plus `x-default`.
- Add build-time regression coverage that fails when sitemap coverage, metadata uniqueness, canonical URLs, structured data, or locale alternate rules drift.

## Capabilities

### New Capabilities
- `book-seo-indexability`: The built bilingual book output publishes crawlable discovery artifacts and page-level SEO signals for landing, chapter, and reference pages without relying on manual post-deploy edits.

### Modified Capabilities
- None.

## Impact

- Affected build scripts are expected to include `scripts/build_site.mjs`, `scripts/build_reader_page_meta.mjs`, and new SEO/sitemap helper scripts under `scripts/` or `scripts/shared/`.
- Affected reader-localization logic includes the current cross-locale mapping in `scripts/localize_reader_shell.mjs`, which must be split into navigation and SEO responsibilities.
- Affected reader-behavior logic includes `theme/custom.js`, which must stop auto-forwarding the book home route to the default chapter.
- Affected tests include metadata/site build assertions such as `tests/test_book_editions.py`, `tests/test_reader_page_meta.py`, and `scripts/test-site-render.sh`.
- Generated output affected after rebuild includes `public/book/**`, `public/fr/book/**`, `public/book-sitemap.xml`, and `public/robots.txt`.
- No new runtime dependencies are required.
