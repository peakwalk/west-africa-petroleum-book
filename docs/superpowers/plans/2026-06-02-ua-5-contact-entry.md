# UA-5 Contact Entry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a consistent mailto-based contact icon to the landing header and mdBook toolbar so users can contact Upstream Atlas from every real top-level navigation surface.

**Architecture:** Keep the feature static and declarative. Extend the shared landing header generator in `scripts/shared/landing-shell.mjs`, extend the mdBook toolbar in `theme/index.hbs`, style both with the existing CSS systems, and lock the contract through `scripts/test-site-render.sh`.

**Tech Stack:** JavaScript template generation, Handlebars, CSS, npm scripts, mdBook static output

---

### Task 1: Lock The UA-5 Contract In Static Tests

**Files:**
- Modify: `scripts/test-site-render.sh`
- Inspect: `scripts/shared/landing-shell.mjs`
- Inspect: `theme/index.hbs`

- [ ] **Step 1: Add failing assertions for the new contact entry**

```sh
check_contains public/index.html 'class="header-contact-link"'
check_contains public/index.html 'mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas'
check_contains public/index.html 'aria-label="Contact Us"'
check_contains public/chapters/index.html 'class="header-contact-link"'
check_contains public/book/index.html 'href="mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas"'
check_contains public/book/index.html 'title="Contact Us"'
check_contains assets/css/landing.css '.header-actions {'
check_contains assets/css/landing.css '.header-contact-link::after {'
```

- [ ] **Step 2: Run the site render test and verify the new assertions fail**

Run: `npm run test:site`
Expected: FAIL because the current headers do not yet render any contact entry.

### Task 2: Add The Contact Action To The Shared Landing Header

**Files:**
- Modify: `scripts/shared/landing-shell.mjs`

- [ ] **Step 1: Add a reusable mailto target constant and render a contact action before the CTA**

```js
const CONTACT_HREF = "mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas";

function renderHeaderContactLink() {
  return `<a class="header-contact-link" href="${CONTACT_HREF}" aria-label="Contact Us" data-tooltip="Contact Us">
    <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
      <path d="M4 7.5h16v9H4z" />
      <path d="m4.75 8 7.25 6 7.25-6" />
    </svg>
  </a>`;
}
```

- [ ] **Step 2: Group the contact action and CTA in the header layout**

```js
<div class="header-actions">
  ${renderHeaderContactLink()}
  <a class="button button-header" href="${escapeHtml(links.ctaHref)}">Start Reading</a>
</div>
```

- [ ] **Step 3: Add the same contact target to the mobile navigation panel**

```js
<a class="mobile-nav-contact" href="${CONTACT_HREF}">Contact Us</a>
<a class="button button-header mobile-nav-cta" href="${escapeHtml(links.ctaHref)}">Start Reading</a>
```

### Task 3: Style The Landing Contact Action For Desktop And Mobile

**Files:**
- Modify: `assets/css/landing.css`

- [ ] **Step 1: Add the header action cluster and icon button treatment**

```css
.header-actions {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.header-contact-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.9rem;
  height: 2.9rem;
  border: 1px solid rgba(49, 99, 194, 0.2);
  border-radius: 999px;
  background: rgba(49, 99, 194, 0.07);
  color: var(--brand-blue-deep);
}
```

- [ ] **Step 2: Add SVG sizing, tooltip, and focus states**

```css
.header-contact-link svg {
  width: 1.1rem;
  height: 1.1rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.header-contact-link::after {
  content: attr(data-tooltip);
  position: absolute;
  inset-inline-end: 50%;
  bottom: calc(100% + 0.5rem);
  transform: translateX(50%);
  padding: 0.45rem 0.6rem;
  border-radius: 0.55rem;
  background: rgba(11, 31, 51, 0.92);
  color: #fff;
  opacity: 0;
}
```

- [ ] **Step 3: Preserve visibility in the mobile breakpoint while hiding only the CTA**

```css
@media (max-width: 900px) {
  .site-header-inner > .button-header {
    display: none;
  }

  .header-actions > .button-header {
    display: none;
  }

  .header-actions {
    justify-self: end;
  }
}
```

### Task 4: Add The Contact Action To The mdBook Toolbar

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`

- [ ] **Step 1: Insert a mailto icon button into `toolbar-right`**

```hbs
<a class="icon-button toolbar-link toolbar-contact-link" href="mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas" title="Contact Us" aria-label="Contact Us">
    {{fa "regular" "envelope"}}
</a>
```

- [ ] **Step 2: Add any minimal CSS needed to keep alignment stable**

```css
#mdbook-menu-bar .book-toolbar .toolbar-contact-link {
  text-decoration: none;
}
```

### Task 5: Verify The Contact Entry End To End

**Files:**
- Inspect: `public/index.html`
- Inspect: `public/chapters/index.html`
- Inspect: `public/book/index.html`

- [ ] **Step 1: Run the site render test and confirm the new contract passes**

Run: `npm run test:site`
Expected: PASS with the contact entry rendered in landing, chapters, and book output.

- [ ] **Step 2: Inspect the generated output for the exact mailto string**

Run: `rg -n "mailto:matt@operatorassetexchange.com\\?subject=Upstream%20Atlas" public/index.html public/chapters/index.html public/book/index.html`
Expected: One or more matches in each generated surface.
