# UA-3 Homepage Iconography Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and integrate a production-grade SVG icon system for the Upstream Atlas homepage, including reusable asset files, a sprite sheet, homepage card icons, country signal icons, and shared CTA/mobile navigation icons.

**Architecture:** Keep the implementation inside the existing static site flow. Store individual SVG sources in `assets/icons/homepage/`, expose them through `assets/icons/homepage-sprite.svg`, wire homepage content and shared shell markup to reference sprite symbols, and extend `scripts/test-site-render.sh` to lock the iconography contract. Keep all paths compatible with home, chapters, and legal pages.

**Tech Stack:** HTML, CSS, SVG, Node static generation scripts, shell-based regression checks

---

## File Structure

- `assets/icons/homepage/`
  Responsibility: source-of-truth individual SVG files for homepage icon assets.
- `assets/icons/homepage-sprite.svg`
  Responsibility: shared sprite sheet referenced by home, chapters, and legal page markup.
- `src/index-main.html`
  Responsibility: homepage-only content blocks including feature cards, country signals, audience cards, and hero CTA.
- `scripts/shared/landing-shell.mjs`
  Responsibility: shared header/footer shell used by `index.html`, `chapters/`, and legal pages.
- `assets/css/landing.css`
  Responsibility: homepage, shared landing shell, and legal/chapter-list icon presentation rules.
- `scripts/test-site-render.sh`
  Responsibility: build-and-assert regression contract for generated public outputs and source assets.

### Task 1: Add Feature Card Icon Assets And Homepage Sprite Foundation

**Files:**
- Create: `assets/icons/homepage/icon-research.svg`
- Create: `assets/icons/homepage/icon-industry-monitoring.svg`
- Create: `assets/icons/homepage/icon-intelligence.svg`
- Create: `assets/icons/homepage-sprite.svg`
- Modify: `src/index-main.html`
- Modify: `assets/css/landing.css`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing test coverage for feature icons and sprite references**

Insert these assertions into `scripts/test-site-render.sh` near the existing landing-page checks:

```sh
check_exists assets/icons/homepage/icon-research.svg
check_exists assets/icons/homepage/icon-industry-monitoring.svg
check_exists assets/icons/homepage/icon-intelligence.svg
check_exists assets/icons/homepage-sprite.svg
check_exists public/assets/icons/homepage/icon-research.svg
check_exists public/assets/icons/homepage/icon-industry-monitoring.svg
check_exists public/assets/icons/homepage/icon-intelligence.svg
check_exists public/assets/icons/homepage-sprite.svg
check_contains public/index.html 'class="feature-card-icon ua-icon ua-icon--feature"'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-research'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-industry-monitoring'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-intelligence'
check_contains assets/css/landing.css '.ua-icon {'
check_contains assets/css/landing.css '.ua-icon--feature {'
check_contains assets/css/landing.css '.feature-card-icon {'
```

- [ ] **Step 2: Run the site regression to verify the new checks fail**

Run: `npm run test:site`

Expected: FAIL with missing icon asset files or missing `feature-card-icon` references in `public/index.html`.

- [ ] **Step 3: Create the three feature SVG files, initialize the sprite, and wire the feature cards**

Create `assets/icons/homepage/icon-research.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M3 8.5 12 3l9 5.5H3Z" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6.5 10v6.5M10.5 10v6.5M14.5 10v3.25" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M4.5 18h8.75" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M14.75 12.5h4.5v3.75h-4.5z" stroke="#1F5E7A" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="18.75" cy="18.25" r="2.25" stroke="#1F5E7A" stroke-width="2"/>
  <path d="m20.35 19.85 1.9 1.9" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-industry-monitoring.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M2.75 19h18.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M4 21c1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M7 18V9.75h4L9.75 5h-1.5L7 9.75M9 9.75h1.25" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M13.25 18V10.25l4.5-4.5h2L16 9.5v8.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M17.75 7.75v4" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-intelligence.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M10.25 4.25c-3.2 0-5.75 2.58-5.75 5.75 0 1.38.5 2.65 1.32 3.64.7.83 1.1 1.84 1.1 2.92v1.19h3.33" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M10.25 4.25V18.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M13 6.5c1.2.8 1.95 2.18 1.95 3.7 0 .97-.3 1.88-.83 2.64" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M14.75 10.25H19.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M14.75 14.5H18" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="20.25" cy="10.25" r="1.25" fill="#D88A1D"/>
  <circle cx="18.75" cy="14.5" r="1.25" fill="#D88A1D"/>
  <circle cx="16.75" cy="18" r="1.25" fill="#D88A1D"/>
  <path d="M12.5 18h3" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage-sprite.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden">
  <symbol id="icon-research" viewBox="0 0 24 24">
    <path d="M3 8.5 12 3l9 5.5H3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M6.5 10v6.5M10.5 10v6.5M14.5 10v3.25" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M4.5 18h8.75" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M14.75 12.5h4.5v3.75h-4.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    <circle cx="18.75" cy="18.25" r="2.25" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="m20.35 19.85 1.9 1.9" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-industry-monitoring" viewBox="0 0 24 24">
    <path d="M2.75 19h18.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M4 21c1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M7 18V9.75h4L9.75 5h-1.5L7 9.75M9 9.75h1.25" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M13.25 18V10.25l4.5-4.5h2L16 9.5v8.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M17.75 7.75v4" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-intelligence" viewBox="0 0 24 24">
    <path d="M10.25 4.25c-3.2 0-5.75 2.58-5.75 5.75 0 1.38.5 2.65 1.32 3.64.7.83 1.1 1.84 1.1 2.92v1.19h3.33" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M10.25 4.25V18.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M13 6.5c1.2.8 1.95 2.18 1.95 3.7 0 .97-.3 1.88-.83 2.64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M14.75 10.25H19.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M14.75 14.5H18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <circle cx="20.25" cy="10.25" r="1.25" fill="#D88A1D"/>
    <circle cx="18.75" cy="14.5" r="1.25" fill="#D88A1D"/>
    <circle cx="16.75" cy="18" r="1.25" fill="#D88A1D"/>
    <path d="M12.5 18h3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </symbol>
</svg>
```

Replace the feature-card portion of `src/index-main.html` with this structure:

```html
<div class="feature-grid">
  <article class="feature-card">
    <svg class="feature-card-icon ua-icon ua-icon--feature" aria-hidden="true" focusable="false">
      <use href="assets/icons/homepage-sprite.svg#icon-research"></use>
    </svg>
    <span class="feature-badge feature-badge-live">Available now</span>
    <p class="feature-kicker">Research</p>
    <h3>Country analysis, petroleum governance, and fiscal frameworks.</h3>
    <p>
      Compare upstream systems, state roles, legal structures, and fiscal
      mechanics across the region with a disciplined editorial baseline.
    </p>
  </article>
  <article class="feature-card">
    <svg class="feature-card-icon ua-icon ua-icon--feature" aria-hidden="true" focusable="false">
      <use href="assets/icons/homepage-sprite.svg#icon-industry-monitoring"></use>
    </svg>
    <span class="feature-badge feature-badge-build">In build</span>
    <p class="feature-kicker">Industry Monitoring</p>
    <h3>Track exploration activity, licensing rounds, and production developments.</h3>
    <p>
      Move beyond static reading into a platform surface that can organise upstream
      events, campaigns, and commercial signals in one place.
    </p>
  </article>
  <article class="feature-card">
    <svg class="feature-card-icon ua-icon ua-icon--feature" aria-hidden="true" focusable="false">
      <use href="assets/icons/homepage-sprite.svg#icon-intelligence"></use>
    </svg>
    <span class="feature-badge">Coming Soon</span>
    <p class="feature-kicker">Intelligence</p>
    <h3>Future AI-powered monitoring of operational, fiscal, and commercial change.</h3>
    <p>
      The homepage now establishes room for premium intelligence workflows without
      overstating capabilities that are still on the roadmap.
    </p>
  </article>
</div>
```

Append these blocks to `assets/css/landing.css` near the existing feature-card rules:

```css
.ua-icon {
  display: inline-block;
  width: 1em;
  height: 1em;
  flex: 0 0 auto;
  color: currentColor;
}

.ua-icon use {
  pointer-events: none;
}

.ua-icon--feature {
  width: 48px;
  height: 48px;
}

.feature-card-icon {
  color: var(--accent);
}
```

- [ ] **Step 4: Run the site regression and verify the feature icon slice passes**

Run: `npm run test:site`

Expected: PASS with the new feature-card icon files copied into `public/assets/icons/homepage/` and the sprite references present in `public/index.html`.

- [ ] **Step 5: Commit the feature icon slice**

```bash
git add assets/icons/homepage/icon-research.svg assets/icons/homepage/icon-industry-monitoring.svg assets/icons/homepage/icon-intelligence.svg assets/icons/homepage-sprite.svg src/index-main.html assets/css/landing.css scripts/test-site-render.sh
git commit -m "feat: add homepage feature card icons"
```

### Task 2: Add Shared CTA And Mobile Navigation Icons

**Files:**
- Create: `assets/icons/homepage/icon-start-reading.svg`
- Create: `assets/icons/homepage/icon-menu.svg`
- Create: `assets/icons/homepage/icon-close.svg`
- Modify: `assets/icons/homepage-sprite.svg`
- Modify: `scripts/shared/landing-shell.mjs`
- Modify: `src/index-main.html`
- Modify: `assets/css/landing.css`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing test coverage for shared CTA and mobile-nav icon references**

Append these checks to `scripts/test-site-render.sh`:

```sh
check_exists assets/icons/homepage/icon-start-reading.svg
check_exists assets/icons/homepage/icon-menu.svg
check_exists assets/icons/homepage/icon-close.svg
check_exists public/assets/icons/homepage/icon-start-reading.svg
check_exists public/assets/icons/homepage/icon-menu.svg
check_exists public/assets/icons/homepage/icon-close.svg
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-start-reading'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-menu'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-close'
check_contains public/index.html 'class="button-icon ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm"'
check_contains public/index.html 'class="mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm"'
check_contains public/chapters/index.html '../assets/icons/homepage-sprite.svg#icon-start-reading'
check_contains assets/css/landing.css '.button-icon {'
check_contains assets/css/landing.css '.mobile-nav-icon-close {'
```

- [ ] **Step 2: Run the site regression to verify the CTA/mobile checks fail**

Run: `npm run test:site`

Expected: FAIL because the new assets and shell markup do not exist yet.

- [ ] **Step 3: Create the shared action icon files, extend the sprite, and update the landing shell**

Create `assets/icons/homepage/icon-start-reading.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M4 12h14" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="m13 7 5 5-5 5" stroke="#D88A1D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

Create `assets/icons/homepage/icon-menu.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M4 7h16M4 12h16M4 17h16" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-close.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="m6 6 12 12M18 6 6 18" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Append these symbols inside `assets/icons/homepage-sprite.svg` before the closing `</svg>`:

```svg
  <symbol id="icon-start-reading" viewBox="0 0 24 24">
    <path d="M4 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="m13 7 5 5-5 5" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </symbol>
  <symbol id="icon-menu" viewBox="0 0 24 24">
    <path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-close" viewBox="0 0 24 24">
    <path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </symbol>
```

Add these helpers near the top of `scripts/shared/landing-shell.mjs`:

```js
function resolveHomepageIconSpriteHref(basePath, iconId) {
  return `${resolveAssetPath(basePath, "assets/icons/homepage-sprite.svg")}#${iconId}`;
}

function renderSpriteIcon({ className, href }) {
  return `<svg class="${escapeHtml(className)}" aria-hidden="true" focusable="false"><use href="${escapeHtml(href)}"></use></svg>`;
}
```

Update `renderLandingHeader` in `scripts/shared/landing-shell.mjs` to compute sprite hrefs and use icon+label markup:

```js
  const startReadingIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-start-reading");
  const menuIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-menu");
  const closeIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-close");
```

```html
          <a class="button button-header" href="${escapeHtml(links.ctaHref)}">
            ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
            <span class="button-label">Start Reading</span>
          </a>
          <details class="mobile-nav-menu">
            <summary class="mobile-nav-toggle">
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm", href: menuIconHref })}
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm", href: closeIconHref })}
              <span class="button-label">Menu</span>
            </summary>
            <nav class="mobile-nav-panel" aria-label="Mobile navigation">
              <a${homeClass} href="${escapeHtml(links.homeHref)}">Home</a>
              <a href="${escapeHtml(links.countriesHref)}">Countries</a>
              <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">Chapters</a>
              <a href="${escapeHtml(links.aboutHref)}">About</a>
              <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
              <a class="mobile-nav-contact" href="${escapeHtml(CONTACT_HREF)}">Contact Us</a>
              <a class="button button-header mobile-nav-cta" href="${escapeHtml(links.ctaHref)}">
                ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
                <span class="button-label">Start Reading</span>
              </a>
            </nav>
          </details>
```

Update the hero CTA in `src/index-main.html` to use the same icon:

```html
<div class="hero-actions">
  <a class="button button-primary" href="book/">
    <svg class="button-icon ua-icon ua-icon--sm" aria-hidden="true" focusable="false">
      <use href="assets/icons/homepage-sprite.svg#icon-start-reading"></use>
    </svg>
    <span class="button-label">Start Reading</span>
  </a>
  <a class="button button-secondary" href="#countries">Explore Country Layer</a>
</div>
```

Append these styles to `assets/css/landing.css` near the existing button and mobile-nav rules:

```css
.ua-icon--sm {
  width: 18px;
  height: 18px;
}

.button-icon {
  color: currentColor;
}

.button-label {
  display: inline-block;
}

.mobile-nav-toggle {
  gap: 0.55rem;
}

.mobile-nav-toggle::after {
  display: none;
}

.mobile-nav-icon-close {
  display: none;
}

.mobile-nav-menu[open] .mobile-nav-icon-menu {
  display: none;
}

.mobile-nav-menu[open] .mobile-nav-icon-close {
  display: inline-block;
}
```

- [ ] **Step 4: Run the site regression and verify the shared-icon slice passes**

Run: `npm run test:site`

Expected: PASS with icon references present in `public/index.html` and `public/chapters/index.html`, and the hero/header/mobile CTA markup rendered with sprite-backed icons.

- [ ] **Step 5: Commit the shared CTA/mobile-nav slice**

```bash
git add assets/icons/homepage/icon-start-reading.svg assets/icons/homepage/icon-menu.svg assets/icons/homepage/icon-close.svg assets/icons/homepage-sprite.svg scripts/shared/landing-shell.mjs src/index-main.html assets/css/landing.css scripts/test-site-render.sh
git commit -m "feat: add shared landing action icons"
```

### Task 3: Add Country Signal And Audience Iconography

**Files:**
- Create: `assets/icons/homepage/icon-production.svg`
- Create: `assets/icons/homepage/icon-exploration.svg`
- Create: `assets/icons/homepage/icon-fiscal.svg`
- Create: `assets/icons/homepage/icon-regulation.svg`
- Create: `assets/icons/homepage/icon-audience-research.svg`
- Create: `assets/icons/homepage/icon-audience-policy.svg`
- Create: `assets/icons/homepage/icon-audience-operators.svg`
- Modify: `assets/icons/homepage-sprite.svg`
- Modify: `src/index-main.html`
- Modify: `assets/css/landing.css`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing test coverage for country signal and audience icon wiring**

Append these checks to `scripts/test-site-render.sh`:

```sh
check_exists assets/icons/homepage/icon-production.svg
check_exists assets/icons/homepage/icon-exploration.svg
check_exists assets/icons/homepage/icon-fiscal.svg
check_exists assets/icons/homepage/icon-regulation.svg
check_exists assets/icons/homepage/icon-audience-research.svg
check_exists assets/icons/homepage/icon-audience-policy.svg
check_exists assets/icons/homepage/icon-audience-operators.svg
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-production'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-exploration'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-fiscal'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-regulation'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-research'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-policy'
check_contains public/index.html 'assets/icons/homepage-sprite.svg#icon-audience-operators'
check_contains public/index.html 'class="country-signal-icon ua-icon ua-icon--sm"'
check_contains public/index.html 'class="country-signal-copy"'
check_contains public/index.html 'class="audience-icon ua-icon ua-icon--audience"'
check_contains assets/css/landing.css '.country-signal-icon {'
check_contains assets/css/landing.css '.country-signal-copy {'
check_contains assets/css/landing.css '.ua-icon--audience {'
```

- [ ] **Step 2: Run the site regression to verify the country/audience checks fail**

Run: `npm run test:site`

Expected: FAIL because the category and audience icon assets do not exist yet and the homepage still uses old country/audience markup.

- [ ] **Step 3: Create category and audience SVG assets, update the sprite, and replace homepage markup**

Create `assets/icons/homepage/icon-production.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M7 4.5h10v12H7z" stroke="#1F5E7A" stroke-width="2" stroke-linejoin="round"/>
  <path d="M7 7.5h10M7 12h10" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 9c1.4 1.35 2.5 2.42 2.5 4A2.5 2.5 0 0 1 12 15.5 2.5 2.5 0 0 1 9.5 13c0-1.58 1.1-2.65 2.5-4Z" fill="#D88A1D"/>
</svg>
```

Create `assets/icons/homepage/icon-exploration.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M2.75 19h18.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M4 21c1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M9 18V10.5h6L13 5h-2l-2 5.5M10.25 12.5h3.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 6.25v3.25" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-fiscal.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M5.5 4.5h8l4 4V19.5h-12z" stroke="#1F5E7A" stroke-width="2" stroke-linejoin="round"/>
  <path d="M13.5 4.5v4h4" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M9 10.25h4.5M9 14h4.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="18.5" cy="16.5" r="3" fill="#D88A1D"/>
  <path d="M18.5 14.75v3.5M17.25 15.75h2.5M17.25 17.25h2.5" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-regulation.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M3 8.5 12 3l9 5.5H3Z" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M6.5 10v7M10.5 10v7M14.5 10v7M17.5 10v7M4.5 18h15" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 5.25h.01" stroke="#D88A1D" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-audience-research.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M5.5 4.5h8.5A2 2 0 0 1 16 6.5v11.25a1.75 1.75 0 0 1-1.75 1.75H7.25A1.75 1.75 0 0 1 5.5 17.75z" stroke="#1F5E7A" stroke-width="2" stroke-linejoin="round"/>
  <path d="M8.25 8.5h5M8.25 11.75h5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="17.75" cy="16.75" r="2.25" stroke="#1F5E7A" stroke-width="2"/>
  <path d="m19.3 18.3 1.7 1.7" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Create `assets/icons/homepage/icon-audience-policy.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M4 7.5h16" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M7 7.5v2.5l-2.5 4h5L7 10M17 7.5v2.5l-2.5 4h5L17 10" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 4v11.5" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M6 18.5h12" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="4" r="1.25" fill="#D88A1D"/>
</svg>
```

Create `assets/icons/homepage/icon-audience-operators.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M7 12a5 5 0 0 1 10 0" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M6 12h12v2.75A2.75 2.75 0 0 1 15.25 17.5h-6.5A2.75 2.75 0 0 1 6 14.75z" stroke="#1F5E7A" stroke-width="2" stroke-linejoin="round"/>
  <path d="M10 17.5v2M14 17.5v2" stroke="#1F5E7A" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 8.25V5.5" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Append these symbols inside `assets/icons/homepage-sprite.svg` before the closing `</svg>`:

```svg
  <symbol id="icon-production" viewBox="0 0 24 24">
    <path d="M7 4.5h10v12H7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    <path d="M7 7.5h10M7 12h10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M12 9c1.4 1.35 2.5 2.42 2.5 4A2.5 2.5 0 0 1 12 15.5 2.5 2.5 0 0 1 9.5 13c0-1.58 1.1-2.65 2.5-4Z" fill="#D88A1D"/>
  </symbol>
  <symbol id="icon-exploration" viewBox="0 0 24 24">
    <path d="M2.75 19h18.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M4 21c1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0 1-.9 2-.9 3 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M9 18V10.5h6L13 5h-2l-2 5.5M10.25 12.5h3.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 6.25v3.25" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-fiscal" viewBox="0 0 24 24">
    <path d="M5.5 4.5h8l4 4V19.5h-12z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    <path d="M13.5 4.5v4h4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M9 10.25h4.5M9 14h4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <circle cx="18.5" cy="16.5" r="3" fill="#D88A1D"/>
    <path d="M18.5 14.75v3.5M17.25 15.75h2.5M17.25 17.25h2.5" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-regulation" viewBox="0 0 24 24">
    <path d="M3 8.5 12 3l9 5.5H3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M6.5 10v7M10.5 10v7M14.5 10v7M17.5 10v7M4.5 18h15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M12 5.25h.01" fill="none" stroke="#D88A1D" stroke-width="2.5" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-audience-research" viewBox="0 0 24 24">
    <path d="M5.5 4.5h8.5A2 2 0 0 1 16 6.5v11.25a1.75 1.75 0 0 1-1.75 1.75H7.25A1.75 1.75 0 0 1 5.5 17.75z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    <path d="M8.25 8.5h5M8.25 11.75h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <circle cx="17.75" cy="16.75" r="2.25" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="m19.3 18.3 1.7 1.7" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-audience-policy" viewBox="0 0 24 24">
    <path d="M4 7.5h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M7 7.5v2.5l-2.5 4h5L7 10M17 7.5v2.5l-2.5 4h5L17 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 4v11.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M6 18.5h12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <circle cx="12" cy="4" r="1.25" fill="#D88A1D"/>
  </symbol>
  <symbol id="icon-audience-operators" viewBox="0 0 24 24">
    <path d="M7 12a5 5 0 0 1 10 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M6 12h12v2.75A2.75 2.75 0 0 1 15.25 17.5h-6.5A2.75 2.75 0 0 1 6 14.75z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
    <path d="M10 17.5v2M14 17.5v2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M12 8.25V5.5" fill="none" stroke="#D88A1D" stroke-width="2" stroke-linecap="round"/>
  </symbol>
```

Update every `.country-signal` in `src/index-main.html` to use this structure:

```html
<div class="country-signal">
  <svg class="country-signal-icon ua-icon ua-icon--sm" aria-hidden="true" focusable="false">
    <use href="assets/icons/homepage-sprite.svg#icon-production"></use>
  </svg>
  <div class="country-signal-copy">
    <span class="country-signal-label">Production</span>
    <span class="country-signal-value">Supply baseline</span>
  </div>
</div>
```

Apply this exact label-to-icon mapping while updating the homepage markup:

| Signal label | Sprite symbol |
| --- | --- |
| `Production`, `Gas`, `Supply` | `icon-production` |
| `Exploration`, `Licensing`, `Blocks`, `Offshore`, `Projects` | `icon-exploration` |
| `Fiscal`, `Revenue`, `Commercial` | `icon-fiscal` |
| `Regulation`, `Governance`, `Policy`, `Operations`, `Infrastructure` | `icon-regulation` |

Replace the three audience icon blocks in `src/index-main.html` with sprite-backed SVGs:

```html
<article class="audience-card">
  <svg class="audience-icon ua-icon ua-icon--audience" aria-hidden="true" focusable="false">
    <use href="assets/icons/homepage-sprite.svg#icon-audience-research"></use>
  </svg>
  <h3>Researchers &amp; Analysts</h3>
  <p>
    A structured base for comparing petroleum governance, upstream phases,
    fiscal systems, and country-specific operating context.
  </p>
</article>
<article class="audience-card">
  <svg class="audience-icon ua-icon ua-icon--audience" aria-hidden="true" focusable="false">
    <use href="assets/icons/homepage-sprite.svg#icon-audience-policy"></use>
  </svg>
  <h3>Policy Teams &amp; Regulators</h3>
  <p>
    A clearer way to navigate licensing, taxation, state participation, and
    institutional capability across West African markets.
  </p>
</article>
<article class="audience-card">
  <svg class="audience-icon ua-icon ua-icon--audience" aria-hidden="true" focusable="false">
    <use href="assets/icons/homepage-sprite.svg#icon-audience-operators"></use>
  </svg>
  <h3>Operators &amp; Advisors</h3>
  <p>
    A high-context reference for commercial positioning, upstream decision
    support, and regional market understanding.
  </p>
</article>
```

Append these styles to `assets/css/landing.css` near the existing audience/country rules:

```css
.ua-icon--audience {
  width: 44px;
  height: 44px;
}

.country-signal {
  grid-template-columns: auto 1fr;
  align-items: start;
  gap: 0.65rem;
}

.country-signal-icon {
  margin-top: 0.12rem;
  color: var(--accent);
}

.country-signal-copy {
  display: grid;
  gap: 0.28rem;
}

.audience-icon {
  color: var(--accent);
}
```

- [ ] **Step 4: Run the site regression and verify the country/audience slice passes**

Run: `npm run test:site`

Expected: PASS with all seven new icon files present, signal icons wired through the sprite, and the audience cards no longer containing inline `<path fill="currentColor">` icon markup.

- [ ] **Step 5: Commit the country/audience slice**

```bash
git add assets/icons/homepage/icon-production.svg assets/icons/homepage/icon-exploration.svg assets/icons/homepage/icon-fiscal.svg assets/icons/homepage/icon-regulation.svg assets/icons/homepage/icon-audience-research.svg assets/icons/homepage/icon-audience-policy.svg assets/icons/homepage/icon-audience-operators.svg assets/icons/homepage-sprite.svg src/index-main.html assets/css/landing.css scripts/test-site-render.sh
git commit -m "feat: add homepage country and audience icons"
```

### Task 4: Run Full Verification And Review Final Scope

**Files:**
- Inspect: `public/index.html`
- Inspect: `public/chapters/index.html`
- Inspect: `public/assets/icons/homepage-sprite.svg`
- Inspect: `public/assets/icons/homepage/`
- Inspect: `assets/css/landing.css`

- [ ] **Step 1: Run the full production build**

Run: `npm run build`

Expected: PASS with `index.html`, legal pages, mdBook output, and `chapters/` regenerated successfully.

- [ ] **Step 2: Run the site regression one more time after the full build**

Run: `npm run test:site`

Expected: PASS with all icon assets copied to `public/assets/icons/homepage/` and all sprite references still resolving correctly in generated outputs.

- [ ] **Step 3: Inspect the working tree and confirm the implementation stayed inside the planned files**

Run: `git status --short`

Expected: either a clean working tree, or only the saved plan document if the implementation run intentionally keeps planning docs uncommitted. Acceptable output:

```text
?? docs/superpowers/plans/2026-06-03-ua-3-homepage-iconography.md
```

- [ ] **Step 4: Review the final diff summary to make sure the change set matches UA-3**

Run: `git diff --stat HEAD~3..HEAD`

Expected: homepage icon assets, sprite, homepage markup, landing shell, landing CSS, and test harness changes only.
