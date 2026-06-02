# UA-2 Homepage Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the Upstream Atlas landing page so it presents as a premium West African petroleum intelligence platform while keeping the existing static site and mdBook workflow intact.

**Architecture:** Keep the implementation constrained to the static landing page surface. Use `scripts/test-site-render.sh` as the regression harness, update `index.html` to introduce the new information architecture, and rebuild `assets/css/landing.css` around the UA-2 typography, palette, and responsive card system.

**Tech Stack:** HTML, CSS, npm scripts, mdBook static output

---

### Task 1: Lock The Homepage Contract In Tests

**Files:**
- Modify: `scripts/test-site-render.sh`
- Inspect: `index.html`
- Inspect: `assets/css/landing.css`

- [ ] **Step 1: Add failing homepage assertions for the new contract**

```sh
check_contains public/index.html 'family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800'
check_contains public/index.html 'href="#countries">Countries</a>'
check_contains public/index.html 'href="#resources">Resources</a>'
check_contains public/index.html 'Platform Intelligence'
check_contains public/index.html 'Country Intelligence'
check_contains public/index.html 'Coming Soon'
check_contains assets/css/landing.css '--primary: #0b1f33;'
check_contains assets/css/landing.css '--secondary: #d88a1d;'
check_contains assets/css/landing.css 'font-family: "Manrope",'
```

- [ ] **Step 2: Run the site render test and verify the new assertions fail**

Run: `npm run test:site`

Expected: FAIL because the existing landing page still references `Lora`, old nav labels, and the old color tokens.

### Task 2: Rebuild The Landing Page Markup

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Replace the header navigation with the UA-2 platform navigation**

```html
<nav class="primary-nav" aria-label="Primary navigation">
  <a class="current-link" href="/">Home</a>
  <a href="#countries">Countries</a>
  <a href="chapters/">Chapters</a>
  <a href="#resources">Resources</a>
  <a href="#about">About</a>
</nav>
<a class="button button-header" href="book/">Start Reading</a>
```

- [ ] **Step 2: Rewrite the hero and add the platform positioning section**

```html
<section class="hero-panel">
  <div class="hero-media" aria-hidden="true"></div>
  <div class="hero-overlay" aria-hidden="true"></div>
  <div class="hero-grid" aria-hidden="true"></div>
  <div class="hero-content">
    <p class="eyebrow">West African Petroleum Intelligence</p>
    <h1>Authority for petroleum governance, upstream activity, and fiscal strategy across West Africa.</h1>
    <p class="hero-copy">A modern reference layer for country analysis, licensing activity, fiscal systems, and operating context across the region.</p>
    <div class="hero-actions">
      <a class="button button-primary" href="book/">Start Reading</a>
      <a class="button button-secondary" href="chapters/">View Chapters</a>
    </div>
  </div>
</section>
<section class="section section-platform">
  <div class="feature-grid">
    <article class="feature-card">
      <p class="feature-kicker">Research</p>
      <h3>Country analysis, petroleum governance, and fiscal frameworks.</h3>
      <p>Structured reference coverage for legal, fiscal, and institutional petroleum questions.</p>
    </article>
  </div>
</section>
```

- [ ] **Step 3: Add the Country Intelligence section and retarget the resources section**

```html
<section id="countries" class="section section-muted">
  <div class="country-grid">
    <article class="country-card">
      <h3>Nigeria</h3>
      <p>Production, exploration, fiscal framework, and regulatory intelligence.</p>
    </article>
  </div>
</section>
<section id="resources" class="section">
  <div class="chapter-preview-grid">
    <article class="chapter-preview-card">
      <p class="chapter-part">Part I: Foundations</p>
      <ul>
        <li><span class="list-chevron" aria-hidden="true">›</span><span><strong>Chapter 1</strong> Value Chain of the Hydrocarbon Sector</span></li>
      </ul>
    </article>
  </div>
</section>
```

### Task 3: Rebuild The Landing Styles

**Files:**
- Modify: `assets/css/landing.css`

- [ ] **Step 1: Replace the top-level design tokens and typography rules**

```css
:root {
  --page-bg: #f7f8f9;
  --surface: #ffffff;
  --surface-muted: #eef2f4;
  --primary: #0b1f33;
  --secondary: #d88a1d;
  --accent: #1f5e7a;
  --text: #102033;
  --text-muted: #526171;
}

html,
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.hero-content h1,
.section-heading h2,
.primary-nav a,
.button,
.feature-card h3,
.country-card h3 {
  font-family: "Manrope", "Inter", sans-serif;
}
```

- [ ] **Step 2: Build the new hero, navigation, feature card, and country card layouts**

```css
.site-header-inner,
.hero-content,
.section-heading,
.feature-grid,
.country-grid,
.editorial-panel,
.audience-grid,
.chapter-preview-grid,
.learning-grid {
  width: min(76rem, calc(100% - 2rem));
  margin: 0 auto;
}

.feature-grid,
.country-grid {
  display: grid;
  gap: 1.25rem;
}

.feature-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.country-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
```

- [ ] **Step 3: Add responsive collapse rules for tablet and mobile**

```css
@media (max-width: 960px) {
  .site-header-inner {
    flex-direction: column;
    align-items: flex-start;
  }

  .feature-grid,
  .country-grid,
  .audience-grid,
  .chapter-preview-grid,
  .learning-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .feature-grid,
  .country-grid,
  .audience-grid,
  .chapter-preview-grid,
  .learning-grid {
    grid-template-columns: 1fr;
  }

  .primary-nav,
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
```

### Task 4: Verify The Homepage Refresh

**Files:**
- Inspect: `public/index.html`
- Inspect: `public/assets/css/landing.css`

- [ ] **Step 1: Run the site render test and confirm it passes**

Run: `npm run test:site`

Expected: PASS with regenerated `public/` output containing the new landing markup and stylesheet tokens.

- [ ] **Step 2: Run the full build and confirm the static site still compiles**

Run: `npm run build`

Expected: PASS with mdBook output and chapters generation succeeding.

- [ ] **Step 3: Review the final diff and keep scope limited to UA-2 homepage work**

Run: `git diff --stat HEAD~1..HEAD`

Expected: homepage markup, landing stylesheet, test harness, and planning docs only.
