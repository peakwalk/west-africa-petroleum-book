# SEO Acceptance Test for `https://upstreamatlas.com/`

## Goal

Use this checklist to verify that SEO changes are not only deployed, but are also visible to Google in a way that can affect crawling, indexing, and search presentation.

For this project, "SEO is working" means four separate things:

1. Public pages return the expected HTML, metadata, canonical URLs, and language signals.
2. Google can fetch and render the live pages.
3. Google has indexed the canonical URLs that we expect it to index.
4. Search Console data starts showing discovery and search activity after deployment.

Do not use `site:upstreamatlas.com` as the only acceptance signal. It is a rough smoke check, not an authoritative test.

## Scope

Run the tests against these URLs at minimum:

- Root site landing page: `https://upstreamatlas.com/`
- English book landing page: `https://upstreamatlas.com/book/`
- French book landing page: `https://upstreamatlas.com/fr/book/`
- Representative deep English chapter:
  `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
- Representative deep French chapter:
  `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`

If a release touched other canonical book pages, include at least one more changed URL per changed page type.

## Preconditions

- The production deployment is complete.
- You have terminal access with `curl`.
- You have Google Search Console access to the `upstreamatlas.com` property.
- You know the production deployment timestamp.

## Pass Criteria

Treat the acceptance result as:

- `PASS`: Technical checks pass, Google live tests pass, indexed results are healthy, and Search Console shows expected crawl/index/search signals.
- `PARTIAL PASS`: Technical checks pass, but Google-side indexing evidence is still pending.
- `FAIL`: Public HTML is wrong, canonical or hreflang is broken, pages are blocked from crawling, or Google reports the wrong canonical/non-indexable verdict.

## Test Cases

### SEO-AT-001 Public availability and HTTP status

Purpose:
Confirm that the URLs are publicly reachable and not blocked by bad status codes or redirect loops.

Steps:

1. Run:

   ```bash
   curl -I https://upstreamatlas.com/
   curl -I https://upstreamatlas.com/book/
   curl -I https://upstreamatlas.com/fr/book/
   curl -I https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html
   curl -I https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html
   ```

2. If any URL returns `301` or `302`, rerun with `-L` and record the final destination:

   ```bash
   curl -sIL https://upstreamatlas.com/book/
   ```

Expected result:

- Canonical destination URLs return `200 OK`.
- There is no redirect loop.
- Deep chapter URLs do not redirect to unrelated pages.

Evidence to save:

- Terminal output for all five requests.

### SEO-AT-002 robots.txt and sitemap exposure

Purpose:
Confirm that Google can discover the sitemap and that the sitemap lists canonical URLs.

Steps:

1. Fetch `robots.txt`:

   ```bash
   curl -sL https://upstreamatlas.com/robots.txt
   ```

2. Confirm that it contains:

   ```text
   Sitemap: https://upstreamatlas.com/book-sitemap.xml
   ```

3. Fetch the sitemap:

   ```bash
   curl -sL https://upstreamatlas.com/book-sitemap.xml
   ```

4. Confirm that it includes:

   - `https://upstreamatlas.com/book/`
   - `https://upstreamatlas.com/fr/book/`
   - representative deep EN/FR chapter URLs

5. Confirm that it does not include redirect shim pages such as:

   - `https://upstreamatlas.com/book/chapters/cover.html`
   - `https://upstreamatlas.com/book/chapters/front-matter.html`
   - `https://upstreamatlas.com/fr/book/chapters/cover.html`
   - `https://upstreamatlas.com/fr/book/chapters/front-matter.html`

Expected result:

- `robots.txt` is public and references the book sitemap.
- The sitemap uses fully-qualified absolute URLs.
- Only canonical URLs meant for search are listed.

Evidence to save:

- `robots.txt` output
- `book-sitemap.xml` output

### SEO-AT-003 Title, description, canonical, and robots directives

Purpose:
Confirm that key metadata is present in the live HTML returned to crawlers.

Steps:

1. Fetch each URL as HTML:

   ```bash
   curl -sL https://upstreamatlas.com/book/ > /tmp/book-en.html
   curl -sL https://upstreamatlas.com/fr/book/ > /tmp/book-fr.html
   curl -sL https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html > /tmp/chapter-en.html
   curl -sL https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html > /tmp/chapter-fr.html
   ```

2. Inspect the head tags:

   ```bash
   rg -n "<title>|meta name=\"description\"|rel=\"canonical\"|name=\"robots\"" /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

3. Verify for each page:

   - one non-empty `<title>`
   - one non-empty `<meta name="description">`
   - one absolute `<link rel="canonical">`
   - no accidental `noindex`

Expected result:

- Metadata exists in the server response HTML.
- Canonical URLs are absolute production URLs.
- No canonical page is blocked by `noindex`.

Evidence to save:

- Extracted tag output per page

### SEO-AT-004 hreflang reciprocity and x-default

Purpose:
Confirm that equivalent language pages point to each other correctly.

Steps:

1. Extract alternate links:

   ```bash
   rg -n 'rel="alternate".*hreflang=' /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

2. Verify that `/book/` and `/fr/book/` each include:

   - self-referencing `hreflang`
   - reciprocal EN/FR alternate
   - `x-default`

3. Verify that the representative EN/FR chapter pair each include:

   - self-referencing `hreflang`
   - reciprocal EN/FR alternate
   - `x-default`

4. For any page without a true translated counterpart, verify:

   - self-referencing `hreflang`
   - `x-default`
   - no fake alternate pointing to a non-equivalent URL

Expected result:

- Equivalent pages are bidirectional.
- Alternate URLs are fully-qualified absolute URLs.
- `x-default` exists on selector-like or fallback pages where expected.

Evidence to save:

- Extracted hreflang lines for each tested page

### SEO-AT-005 Structured data presence and consistency

Purpose:
Confirm that structured data is present and describes the visible page content, not unrelated hidden content.

Steps:

1. Extract JSON-LD blocks:

   ```bash
   rg -n "application/ld\\+json|@type|\"url\"|\"name\"|\"inLanguage\"" /tmp/book-en.html /tmp/book-fr.html /tmp/chapter-en.html /tmp/chapter-fr.html
   ```

2. Verify:

   - `/book/` and `/fr/book/` expose `Book` JSON-LD
   - numbered chapter pages expose `Chapter` and `BreadcrumbList`
   - schema `url` values match canonical URLs
   - schema language and page language are consistent with the visible page

Expected result:

- JSON-LD is present in the page HTML.
- The schema is page-appropriate and matches visible content.

Evidence to save:

- Extracted JSON-LD snippets

### SEO-AT-006 Static crawlable content in raw HTML

Purpose:
Confirm that important content is visible in the raw HTML, not only after client-side JavaScript runs.

Steps:

1. Inspect the raw HTML of the representative chapter pages:

   ```bash
   rg -n "<h1|Hydrocarbon Value Chain|value chain comprises three principal segments" /tmp/chapter-en.html
   rg -n "<h1|chaîne de valeur|secteur pétrolier" /tmp/chapter-fr.html
   ```

2. Open the same URLs in a browser and confirm the visible content matches the raw HTML.

Expected result:

- The chapter H1 is present in raw HTML.
- At least one representative body paragraph is present in raw HTML.
- The rendered browser page is materially consistent with the raw HTML.

Evidence to save:

- Terminal output showing H1/body text in raw HTML
- Browser screenshots of the rendered page

### SEO-AT-007 Search Console URL Inspection: indexed result

Purpose:
Confirm what Google currently knows about the URL in the index. This is stronger than a raw HTTP check.

Steps:

1. Open Search Console for the `upstreamatlas.com` property.
2. Inspect each of these URLs:

   - `https://upstreamatlas.com/`
   - `https://upstreamatlas.com/book/`
   - `https://upstreamatlas.com/fr/book/`
   - representative deep EN chapter
   - representative deep FR chapter

3. Record for each URL:

   - whether the status starts with `URL is on Google`
   - the user-declared canonical
   - the Google-selected canonical
   - whether crawling and indexing are allowed
   - whether the page was found in the submitted sitemap

Expected result:

- Canonical pages are indexable.
- User-declared canonical and Google-selected canonical match, or any mismatch is explainable and accepted.
- Sitemap association is present for canonical URLs.

Evidence to save:

- Screenshot of the indexed result panel per URL

### SEO-AT-008 Search Console URL Inspection: live test

Purpose:
Confirm that Google can fetch and render the live page right now. This is required because a valid deployment alone does not prove Google can access the page.

Steps:

1. For the same URLs in Search Console, click `Test live URL`.
2. Wait for the live test to complete.
3. Record:

   - live verdict
   - crawl allowed?
   - page fetch
   - indexing allowed?
   - screenshot availability

4. Open `View tested page` and capture:

   - screenshot
   - raw HTML
   - HTTP response headers
   - page resources

5. In the returned HTML, confirm that title, canonical, hreflang, and representative body text are present.

Expected result:

- Live test verdict is `URL is available to Google` or `URL is available to Google, but has issues` only if the issue is understood and non-blocking.
- Google can fetch the page and render a screenshot.
- Raw HTML seen by Google contains the same SEO-critical signals as the public HTML check.

Evidence to save:

- Screenshot of live test verdict
- Screenshot of rendered page from Search Console
- Saved raw HTML from `View tested page`

### SEO-AT-009 Search Console sitemap submission

Purpose:
Confirm that Google has seen the sitemap and is processing it normally.

Steps:

1. Open Search Console > Sitemaps.
2. Submit `https://upstreamatlas.com/book-sitemap.xml` if it has not been submitted yet.
3. Record:

   - submission timestamp
   - fetch status
   - discovered URLs count
   - last read timestamp

Expected result:

- Sitemap submission is accepted.
- Search Console can fetch the sitemap.
- There is no parse error or access error.

Evidence to save:

- Screenshot of the sitemap details page

### SEO-AT-010 Search Console page indexing health

Purpose:
Catch cases where pages are technically reachable but still not being indexed correctly.

Steps:

1. Open Search Console > Page indexing.
2. Filter to URLs under:

   - `/book/`
   - `/fr/book/`

3. Review whether representative pages appear in excluded states such as:

   - `Discovered - currently not indexed`
   - `Crawled - currently not indexed`
   - `Duplicate, Google chose different canonical than user`
   - `Alternate page with proper canonical tag`

4. For any excluded representative URL, drill in and inspect the URL.

Expected result:

- Canonical target pages are not stuck in exclusion states without explanation.
- Excluded pages are only the ones intentionally excluded, such as redirect shims or non-canonical duplicates.

Evidence to save:

- Screenshot of the Page indexing summary
- Notes on any excluded URLs

### SEO-AT-011 Search performance trend after deployment

Purpose:
Verify that the technical SEO changes are starting to produce discovery or search activity. This is the only part that checks "effect" rather than just "correct implementation".

Steps:

1. Wait until at least one full recrawl/indexing cycle has happened. In practice, review at:

   - T+3 days
   - T+7 days
   - T+28 days

2. Open Search Console > Performance > Search results.
3. Apply filters:

   - Page contains `/book/` for English
   - Page contains `/fr/book/` for French

4. Compare the post-release window against the pre-release window for:

   - impressions
   - clicks
   - average position
   - indexed page coverage trends

5. Record changes for the representative deep chapter URLs and book landing pages.

Expected result:

- Impressions for canonical book pages are non-zero after indexing.
- There is no sustained post-release collapse in indexed pages or impressions caused by the release.
- If traffic is small, discovery may show up before clicks; that still counts as early positive evidence.

Evidence to save:

- Exported Search Console performance CSV
- Before/after screenshots

## Decision Rules

Use these rules when writing the final acceptance verdict:

- If SEO-AT-001 through SEO-AT-006 fail, the release is not SEO-ready.
- If SEO-AT-001 through SEO-AT-006 pass but SEO-AT-007 through SEO-AT-010 are incomplete, mark the release as technically correct but not fully SEO-accepted.
- If SEO-AT-001 through SEO-AT-010 pass, the SEO implementation is accepted.
- SEO-AT-011 is a trailing effectiveness check. It should be tracked after release, but it should not block deployment if the technical and indexing checks already pass.

## Fast Handoff Checklist

Use this shortened checklist when handing the final Google-side validation to someone who has Search Console access.

### Handoff Inputs

- Property: `upstreamatlas.com`
- Release date: fill in the production release timestamp
- URLs to inspect:
  - `https://upstreamatlas.com/book/`
  - `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
  - `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
- Sitemap to submit or verify:
  - `https://upstreamatlas.com/book-sitemap.xml`

### 5-Minute Search Console Checklist

1. Open Search Console and submit or verify `https://upstreamatlas.com/book-sitemap.xml`.
2. Run URL Inspection for the three URLs above and capture the indexed result:
   - `URL is on Google` or current status
   - user-declared canonical
   - Google-selected canonical
   - whether the page was found in the sitemap
3. Run `Test live URL` for the same three URLs and capture:
   - live verdict
   - screenshot
   - tested HTML
4. Open Page indexing and check whether the representative URLs are stuck in:
   - `Discovered - currently not indexed`
   - `Crawled - currently not indexed`
   - `Duplicate, Google chose different canonical than user`
5. After T+7 and T+28, open Performance > Search results and compare post-release impressions for `/book/` and `/fr/book/`.

### Jira Evidence Template

Paste this into the Jira issue after the Search Console checks are complete:

```md
Search Console follow-up completed on YYYY-MM-DD.

Sitemap
- `https://upstreamatlas.com/book-sitemap.xml`
- Status:
- Last read:
- Any parse/fetch issues:

URL Inspection
- `/book/`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:
- EN representative chapter
  - URL: `https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:
- FR representative chapter
  - URL: `https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - Indexed result:
  - User canonical:
  - Google canonical:
  - Found in sitemap:

Live Test
- `/book/`:
- EN representative chapter:
- FR representative chapter:

Page Indexing Notes
- Any exclusion state observed:
- Any canonical mismatch observed:

Performance Follow-up
- T+7 impressions trend:
- T+28 impressions trend:

Final Verdict
- PASS / PARTIAL PASS / FAIL
- Notes:
```

## Notes

- A passing live test does not guarantee indexing. Google states that the live URL test only confirms that Google can access the page for indexing, not that the page will definitely be indexed.
- For multilingual pages, Google recommends explicit alternate mapping and requires each language version to list itself and the other versions. Use `hreflang` to express equivalence, not to force language detection.
- Structured data is useful because it helps Google understand the page, but it must describe the visible content of that page.

## Reference Links

- Google Search Central: [Tell Google about localized versions of your page](https://developers.google.com/search/docs/specialty/international/localized-versions)
- Google Search Central: [Introduction to structured data markup](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- Google Search Central: [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- Search Console Help: [URL Inspection tool](https://support.google.com/webmasters/answer/9012289?hl=en)
