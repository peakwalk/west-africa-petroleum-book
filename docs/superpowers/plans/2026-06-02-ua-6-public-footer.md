# UA-6 Public Footer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete shared footer to the public landing surfaces and placeholder website legal pages while intentionally excluding mdBook reader pages from footer rendering.

**Architecture:** Keep footer rendering inside the landing shell only. Centralize footer data and legal URLs in `scripts/shared/landing-shell.mjs`, generate placeholder website legal pages with a dedicated script, style both through landing-specific CSS, and lock the boundary with static render tests that assert landing pages have the footer and mdBook pages do not.

**Tech Stack:** Node.js static generation, HTML template strings, CSS, mdBook build pipeline, shell-based render assertions

---

### Task 1: Lock The New Footer Contract In Static Tests

**Files:**
- Modify: `scripts/test-site-render.sh`
- Inspect: `scripts/shared/landing-shell.mjs`
- Inspect: `theme/index.hbs`

- [ ] **Step 1: Add failing assertions for public footer coverage and mdBook exclusion**

```sh
check_contains public/index.html 'class="site-footer site-footer-detailed"'
check_contains public/index.html 'Terms of Use'
check_contains public/index.html 'Privacy Policy'
check_contains public/index.html 'Cookie Policy'
check_contains public/chapters/index.html 'class="site-footer site-footer-detailed"'
check_contains public/chapters/index.html 'mailto:matt@operatorassetexchange.com'
check_exists public/terms-of-use.html
check_exists public/privacy-policy.html
check_exists public/cookie-policy.html
check_contains public/terms-of-use.html 'class="legal-page"'
check_contains public/privacy-policy.html 'class="legal-page"'
check_contains public/cookie-policy.html 'class="legal-page"'
check_not_contains public/book/index.html 'site-footer-detailed'
check_not_contains public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html 'site-footer-detailed'
```

- [ ] **Step 2: Run the render test and verify the new assertions fail**

Run: `npm run test:site`
Expected: FAIL because the current build does not generate the detailed footer or legal pages.

### Task 2: Centralize Footer Data In The Landing Shell

**Files:**
- Modify: `scripts/shared/landing-shell.mjs`

- [ ] **Step 1: Add canonical website legal URLs and footer data structures**

```js
const WEBSITE_LEGAL_LINKS = {
  terms: "terms-of-use.html",
  privacy: "privacy-policy.html",
  cookie: "cookie-policy.html",
};

const FOOTER_COLUMNS = [
  {
    title: "Upstream Atlas",
    body:
      "Practical insights into the technical, commercial, fiscal, regulatory, and governance aspects of the West African oil and gas industry.",
  },
  {
    title: "Explore",
    links: [
      { label: "Home", hrefKey: "homeHref" },
      { label: "About", hrefKey: "aboutHref" },
      { label: "Countries", hrefKey: "countriesHref" },
      { label: "Book Contents", hrefKey: "chaptersHref" },
      { label: "Contact", href: CONTACT_HREF },
    ],
  },
];
```

- [ ] **Step 2: Extend link resolution so landing pages can reach legal pages from both root and `chapters/`**

```js
function resolveShellLinks(currentPage) {
  if (currentPage === "chapters") {
    return {
      // existing fields...
      termsHref: "../terms-of-use.html",
      privacyHref: "../privacy-policy.html",
      cookieHref: "../cookie-policy.html",
    };
  }

  return {
    // existing fields...
    termsHref: "terms-of-use.html",
    privacyHref: "privacy-policy.html",
    cookieHref: "cookie-policy.html",
  };
}
```

- [ ] **Step 3: Replace the simplified footer with a detailed footer renderer**

```js
export function renderLandingFooter({ currentPage = "home", logoBasePath = "" } = {}) {
  const links = resolveShellLinks(currentPage);

  return `    <footer class="site-footer site-footer-detailed">
      <div class="site-footer-inner">
        <!-- render four footer columns here -->
      </div>
      <div class="site-footer-bottom">
        <p>© 2026 Upstream Atlas. All Rights Reserved.</p>
        <p>West Africa Oil &amp; Gas Intelligence</p>
      </div>
    </footer>`;
}
```

### Task 3: Build Placeholder Website Legal Pages As Real Static Outputs

**Files:**
- Create: `scripts/generate-legal-pages.mjs`
- Create: `src/legal/terms-of-use.json`
- Create: `src/legal/privacy-policy.json`
- Create: `src/legal/cookie-policy.json`

- [ ] **Step 1: Create structured placeholder legal content source files**

```json
{
  "title": "Terms of Use",
  "statusLine": "Status: Final approved text pending publication",
  "updatedAt": "Last updated: 2026-06-02",
  "noticeTitle": "Document pending final approved text",
  "noticeBody": "This page reserves the canonical legal URL and will be replaced in place once the approved text is ready.",
  "statusItems": [
    "Canonical public URL reserved.",
    "Approved legal text pending publication."
  ],
  "sections": [
    {
      "heading": "Why this page exists",
      "paragraphs": [
        "This placeholder preserves a stable legal URL without publishing unapproved final legal wording."
      ]
    }
  ]
}
```

- [ ] **Step 2: Add a static generator that renders the three placeholder website legal pages**

```js
const PAGES = [
  { slug: "terms-of-use", source: "terms-of-use.json" },
  { slug: "privacy-policy", source: "privacy-policy.json" },
  { slug: "cookie-policy", source: "cookie-policy.json" },
];

async function buildLegalPage(page) {
  const content = JSON.parse(await fs.readFile(sourcePath, "utf8"));
  const html = `<!doctype html>
<html lang="en">
  <head>...</head>
  <body class="legal-page">
    <main class="legal-page-main">...</main>
    ${renderLandingFooter({ currentPage: "legal" })}
  </body>
</html>`;
}
```

- [ ] **Step 3: Render only website-group legal links inside the legal page header**

```js
function renderLegalNav(currentSlug) {
  return `
    <nav class="legal-page-nav" aria-label="Legal documents">
      <a href="terms-of-use.html"${currentSlug === "terms-of-use" ? ' aria-current="page"' : ""}>Terms of Use</a>
      <a href="privacy-policy.html"${currentSlug === "privacy-policy" ? ' aria-current="page"' : ""}>Privacy Policy</a>
      <a href="cookie-policy.html"${currentSlug === "cookie-policy" ? ' aria-current="page"' : ""}>Cookie Policy</a>
    </nav>`;
}
```

### Task 4: Style The Detailed Footer And Legal Pages

**Files:**
- Modify: `assets/css/landing.css`
- Create: `assets/css/legal.css`

- [ ] **Step 1: Add detailed footer layout styles**

```css
.site-footer-detailed {
  padding: 3.5rem 0 1.4rem;
  background: linear-gradient(180deg, rgba(6, 19, 35, 0.96), rgba(11, 31, 51, 1));
  color: rgba(255, 255, 255, 0.82);
}

.site-footer-inner {
  width: min(76rem, calc(100% - 2rem));
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
}
```

- [ ] **Step 2: Add link, future-item, and contact styles**

```css
.site-footer-column-links,
.site-footer-contact-list {
  display: grid;
  gap: 0.65rem;
}

.site-footer-future-item {
  color: rgba(255, 255, 255, 0.52);
}
```

- [ ] **Step 3: Add legal page shell styling and responsive breakpoints**

```css
.legal-page {
  background: #f6f8fb;
  color: #13233f;
}

.legal-page-main {
  width: min(52rem, calc(100% - 2rem));
  margin: 0 auto;
  padding: 3rem 0 4rem;
}
```

### Task 5: Wire Legal Page Generation Into The Build

**Files:**
- Modify: `package.json`

- [ ] **Step 1: Add a dedicated legal build script**

```json
"build:legal": "node scripts/generate-legal-pages.mjs"
```

- [ ] **Step 2: Run the legal generator in both normal build and site export**

```json
"build": "npm run build:index && npm run build:legal && mdbook build && npm run build:chapters",
"build:site": "rm -rf public && mkdir -p public && npm run build:index && npm run build:legal && npm run build:chapters && cp index.html public/index.html && cp terms-of-use.html public/terms-of-use.html && cp privacy-policy.html public/privacy-policy.html && cp cookie-policy.html public/cookie-policy.html && cp -R assets public/assets && cp -R chapters public/chapters && mdbook build --dest-dir public/book"
```

### Task 6: Verify The Public Footer End To End

**Files:**
- Inspect: `public/index.html`
- Inspect: `public/chapters/index.html`
- Inspect: `public/terms-of-use.html`
- Inspect: `public/book/index.html`

- [ ] **Step 1: Run the full site render verification**

Run: `npm run test:site`
Expected: PASS with detailed footer coverage on landing pages and placeholder legal pages, and no landing footer markers inside mdBook pages.

- [ ] **Step 2: Verify canonical legal URLs and mdBook exclusion explicitly**

Run: `rg -n "terms-of-use\\.html|privacy-policy\\.html|cookie-policy\\.html|site-footer-detailed" public/index.html public/chapters/index.html public/terms-of-use.html public/privacy-policy.html public/cookie-policy.html public/book/index.html public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
Expected: legal URLs and footer markers appear on landing/legal pages only; `site-footer-detailed` does not appear in mdBook output.
