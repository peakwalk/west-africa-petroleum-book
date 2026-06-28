## ADDED Requirements

### Requirement: Book output MUST publish crawlable discovery artifacts
The site build SHALL generate a root `book-sitemap.xml` that lists canonical English and French book URLs, and a root `robots.txt` that references that sitemap. Redirect-only pages such as `chapters/front-matter.html` MUST NOT appear in the sitemap inventory.

#### Scenario: Sitemap includes bilingual canonical book URLs
- **WHEN** `npm run build:site` completes
- **THEN** `public/book-sitemap.xml` exists
- **THEN** it contains absolute URLs for `https://upstreamatlas.com/book/`, `https://upstreamatlas.com/fr/book/`, and each canonical content page under those roots
- **THEN** it omits redirect-only pages such as `https://upstreamatlas.com/book/chapters/front-matter.html`

#### Scenario: robots.txt references the book sitemap
- **WHEN** `npm run build:site` completes
- **THEN** `public/robots.txt` exists
- **THEN** it includes `Sitemap: https://upstreamatlas.com/book-sitemap.xml`

### Requirement: Canonical book pages MUST publish unique canonical metadata
Each canonical book landing, chapter, and reference page SHALL emit a non-empty `<title>`, a non-empty `<meta name="description">`, and an absolute `<link rel="canonical">`. Canonical pages within the same locale MUST NOT share duplicate title-and-description pairs.

#### Scenario: English chapter page emits unique absolute metadata
- **WHEN** the build publishes an English canonical chapter page
- **THEN** its `<head>` includes a non-empty `<title>` ending in `| Upstream Atlas`
- **THEN** its description meta content is non-empty
- **THEN** its canonical href is an absolute `https://upstreamatlas.com/book/...` URL

#### Scenario: French book landing page emits unique absolute metadata
- **WHEN** the build publishes `https://upstreamatlas.com/fr/book/`
- **THEN** its `<head>` includes a non-empty title and non-empty description
- **THEN** its canonical href equals `https://upstreamatlas.com/fr/book/`

### Requirement: Canonical book landing pages MUST remain stable cover destinations
The canonical `/book/` and `/fr/book/` landing pages SHALL render the cover experience in place and MUST NOT immediately client-side redirect to a default chapter. Explicit cover CTAs MAY continue to link to the intended first reading chapter for each locale.

#### Scenario: Book root stays on cover while preserving explicit reading entry
- **WHEN** a user opens `https://upstreamatlas.com/book/` or `https://upstreamatlas.com/fr/book/`
- **THEN** the published page remains on the cover route instead of automatically forwarding to a chapter URL
- **THEN** the cover UI still includes an explicit reading CTA that links to the locale-appropriate first chapter

### Requirement: Canonical book pages MUST publish locale alternates only for equivalent pages
Every canonical book page SHALL emit a self-referencing `hreflang` link and an `x-default` link. Pages with confirmed EN/FR equivalence MUST emit reciprocal alternate links to each other. Pages without a confirmed counterpart MUST NOT emit a non-equivalent alternate link.

#### Scenario: Equivalent chapter pages emit reciprocal alternates
- **WHEN** a canonical English chapter has a confirmed French counterpart
- **THEN** the English page emits `hreflang="en"`, `hreflang="fr"`, and `hreflang="x-default"`
- **THEN** the French counterpart emits reciprocal `hreflang="fr"` and `hreflang="en"` links back to the English page

#### Scenario: English-only pages keep self-reference plus x-default
- **WHEN** a canonical English book page does not have a confirmed French counterpart
- **THEN** the page emits its self-referencing `hreflang="en"` link
- **THEN** the page emits `hreflang="x-default"` pointing to its own canonical URL
- **THEN** the page does not emit a French alternate pointing at `/fr/book/` or any other non-equivalent URL

### Requirement: Canonical book pages MUST publish structured data appropriate to page type
Book landing pages SHALL emit `Book` JSON-LD. Numbered chapter pages SHALL emit `Chapter` plus `BreadcrumbList` JSON-LD. Canonical reference pages SHALL emit `WebPage` plus `BreadcrumbList` JSON-LD. All structured-data URLs MUST use the page’s absolute canonical URL.

#### Scenario: Book landing page emits Book schema
- **WHEN** the build publishes `/book/`
- **THEN** its `<head>` includes one `application/ld+json` block with `@type` set to `Book`
- **THEN** the schema includes the page canonical URL, `Upstream Atlas` publisher data, and bilingual language metadata

#### Scenario: Numbered chapter page emits Chapter and breadcrumb schema
- **WHEN** the build publishes a numbered chapter page such as `/book/chapters/chapter-05-hydrocarbon-value-chain.html`
- **THEN** its `<head>` includes structured data for both `Chapter` and `BreadcrumbList`
- **THEN** each schema entry uses the page’s absolute canonical URL

#### Scenario: Reference page emits WebPage and breadcrumb schema
- **WHEN** the build publishes a canonical reference page such as `/fr/book/chapters/glossary.html`
- **THEN** its `<head>` includes structured data for `WebPage` and `BreadcrumbList`
- **THEN** it does not mislabel the page as a numbered `Chapter`

### Requirement: SEO hardening MUST preserve static crawlable chapter content
The SEO hardening pass MUST remain additive to the generated HTML and MUST NOT move chapter body content behind client-side JavaScript. Representative chapter pages SHALL still contain their chapter heading and body text in static markup after the SEO pass runs.

#### Scenario: Static chapter body remains visible after SEO injection
- **WHEN** the build publishes a representative chapter page
- **THEN** the HTML still contains the chapter H1 and body paragraph text in the server-generated markup
- **THEN** search-engine-critical content is not deferred to client-side script execution
