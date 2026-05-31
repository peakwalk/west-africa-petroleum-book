# Landing And Book Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the landing page and mdBook reading shell so both match the approved prototype direction while preserving the existing static Markdown publishing workflow.

**Architecture:** Keep the current split between a static landing page and an mdBook-generated book. Port the prototype’s visual language into `index.html`/`assets/css/landing.css`, then override mdBook theme templates so the book shell follows the prototype reading experience without replacing the content pipeline.

**Tech Stack:** HTML, CSS, mdBook theme overrides, vanilla JavaScript

---

### Task 1: Rebuild The Landing Page

**Files:**
- Modify: `index.html`
- Modify: `assets/css/landing.css`

- [ ] Rewrite the landing page markup so it mirrors the prototype sections and links into the real static book output.
- [ ] Replace the landing stylesheet with the shared blue/orange visual language, responsive navigation, hero treatment, card grid, chapter previews, and footer styling.
- [ ] Keep GA wiring and document-relative asset paths intact.

### Task 2: Replace The mdBook Reading Shell

**Files:**
- Create: `theme/index.hbs`
- Create: `theme/book.js`
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`

- [ ] Override the mdBook shell with a custom Handlebars template that preserves mdBook features while changing the toolbar and page layout.
- [ ] Add shell JavaScript for progress indication and any layout glue not already handled by mdBook.
- [ ] Rework the book stylesheet so sidebar, toolbar, content column, right rail, tables, and chapter navigation match the prototype reading page.
- [ ] Keep or trim the existing scroll bridge only if the new shell still needs it.

### Task 3: Verify Generated Output

**Files:**
- Inspect: `public/index.html`
- Inspect: `public/book/index.html`
- Inspect: `public/book/chapters/*.html`

- [ ] Run `npm run build` and confirm the landing page and book both generate successfully.
- [ ] Inspect the generated HTML structure to confirm the custom theme is present.
- [ ] Review the final diff for unintended changes outside the approved scope.
