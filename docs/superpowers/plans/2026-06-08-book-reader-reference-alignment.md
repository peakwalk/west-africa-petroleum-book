# Book Reader Reference Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved wide-screen and narrow-screen reader references in the mdBook reader so the live `/book/` experience matches the intended academic-monograph shell, navigation hierarchy, logo behavior, and knowledge-object styling without breaking mdBook as the content engine.

**Architecture:** Keep `theme/index.hbs` as the only reader-shell template, `theme/custom.css` as the single source of truth for layout tokens and responsive component styling, and `theme/custom.js` as a thin DOM-orchestration layer for derived mobile chrome, outline placement, and figure/table enhancements. Do not chase the mock literally where source content differs; instead project the approved design system onto the real book structure and verify it on representative figure, table, and formula chapters.

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions

---

## First Principles

1. **Reading is primary.** The reader opens the book to read long-form content; navigation and utilities exist to reduce cognitive load, not compete for attention.
2. **Brand continuity must signal trust, not novelty.** The reader header must use the same `Upstream Atlas` asset family as the landing page. The book is a continuation of the same product, not a separate property.
3. **Knowledge objects need stable semantics.** Formulas, figures, and tables are not decorative blocks; they are scholarly reference objects with captions, notes, and cross-device continuity.
4. **Responsive behavior must preserve semantics.** Mobile is a transformation of the same reader, not a second product. The same objects should survive across breakpoints with different containment and navigation affordances.
5. **Source fidelity beats mock literalism.** The approved screenshots are reference designs for shell, hierarchy, and component treatment. When the live chapter corpus differs from mock copy or object order, keep the design system and map it onto the real chapter content instead of inventing new editorial content.

## MECE Workstreams

1. **Reader Shell And Brand**
   - Header, logo sizing, sidebar, progress bar, page background, pagination shell.
2. **Navigation And Orientation**
   - Desktop sidebar behavior, desktop outline rail, mobile chapter bar, mobile inline “On this page”.
3. **Knowledge Object System**
   - Formula panels, figure cards, table cards, captions, notes, text-image pairings.
4. **Responsive Transformations**
   - Desktop-to-tablet-to-mobile layout rules, preserved component identity, density tuning.
5. **Verification And Release Safety**
   - Source assertions, generated-output assertions, manual visual QA on representative chapters.

## Non-Goals

- Do not edit `public/` by hand.
- Do not rewrite the landing page.
- Do not change the chapter corpus merely to force the exact mock title “Overview of the Upstream Petroleum Industry”.
- Do not invent net-new chapter-level formulas if the implementation can satisfy formula design using already-authored formula surfaces.
- Do not replace mdBook navigation, search, or content generation with a client framework.

## Source Reality vs. Mock Reality

The approved wide and narrow references depict a conceptual chapter page. The live repository does **not** contain that exact chapter title. The nearest implementation strategy is:

- use the references as the source of truth for shell, brand, layout, and object treatment
- validate shell + figures + tables on `chapter-01-value-chain-of-the-hydrocarbon-sector`
- validate formula treatment on `glossary`, `chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states`, and `chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries`

If product wants a formula block injected into `chapter-01` later, treat that as a **separate editorial/parity decision**, not part of this shell-alignment plan.

## File Map

- `theme/index.hbs:127-239`
  - Owns the static reader shell and must expose placeholders for mobile-only derived chrome.
- `theme/custom.css:17-224`
  - Owns global reader tokens, shell geometry, typography, and light-theme palette defaults.
- `theme/custom.css:549-910`
  - Owns toolbar, logo sizing, search slot, sidebar, outline rail, and pagination card styling.
- `theme/custom.css:1347-1888`
  - Owns formulas, figures, tables, captions, and scholarly object styling.
- `theme/custom.css:1925-2023`
  - Owns breakpoint-driven collapse behavior for outline, pagination, and header logo switching.
- `theme/custom.js:159-650`
  - Owns outline normalization, figure/table wrapping, search-slot orchestration, and page-variant glue.
- `scripts/test-site-render.sh:407-1035`
  - Owns build-time contract assertions for source files and generated book output.
- **Representative generated acceptance surfaces**
  - `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
  - `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `public/book/chapters/glossary.html`

## Visual Contract To Implement

### Desktop / Wide Reference

- Full landing-page-consistent `Upstream Atlas` lockup in the header.
- Left chapter rail remains the primary navigation object.
- Center reading column stays visually dominant.
- Right rail becomes a quiet “On This Page” reference panel.
- Formula blocks, figure cards, and table cards share one academic publication language.

### Narrow / Mobile Reference

- Same brand family, but use the compact icon in the header.
- Under-header chapter context bar replaces always-visible sidebar.
- “On This Page” becomes an inline card inside article flow.
- Figures and tables keep the same card identity as desktop, not a separate mobile style family.
- Mobile keeps the academic tone by compressing density, not by flattening objects.

---

### Task 1: Lock The Reference Contract In The Render Test

**Files:**
- Modify: `scripts/test-site-render.sh`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing assertions for the new shell placeholders and responsive contract**

Add assertions near the existing `public/book/index.html`, `theme/index.hbs`, `theme/custom.css`, and `theme/custom.js` checks:

```sh
check_contains theme/index.hbs 'class="reader-mobile-chapter-bar hidden"'
check_contains theme/index.hbs 'class="reader-mobile-chapter-toggle"'
check_contains theme/index.hbs 'class="reader-mobile-outline-anchor"'
check_contains theme/custom.css '.reader-mobile-chapter-bar {'
check_contains theme/custom.css '.reader-mobile-chapter-toggle {'
check_contains theme/custom.css '.reader-mobile-outline-card {'
check_contains theme/custom.css '.reader-mobile-outline-card .on-this-page {'
check_contains theme/custom.js 'function installMobileChapterBar()'
check_contains theme/custom.js 'function installInlineOutlineCard()'
check_contains theme/custom.js 'document.querySelector(".reader-mobile-chapter-toggle")'
check_contains theme/custom.js 'document.querySelector(".reader-mobile-outline-anchor")'
check_contains theme/custom.css '--brand-blue: #3163c2;'
check_contains theme/custom.css '--brand-blue-deep: #264d97;'
check_contains theme/custom.css '--brand-gold: #d9b24a;'
```

- [ ] **Step 2: Add contract checks that the same logo family remains present in the generated book shell**

Keep the current logo-asset assertions and add desktop/mobile size checks in the source CSS:

```sh
check_contains theme/custom.css '.book-home-icon-full {'
check_contains theme/custom.css 'width: 138px;'
check_contains theme/custom.css '.book-home-icon-compact {'
check_contains theme/custom.css 'width: 24px;'
check_contains theme/custom.css 'height: 24px;'
```

- [ ] **Step 3: Run the site render test to verify it fails on the new mobile-shell requirements**

Run:

```bash
npm run test:site
```

Expected: FAIL with a missing pattern such as `class="reader-mobile-chapter-bar hidden"` or `.reader-mobile-outline-card {`, proving the new contract is enforced.

- [ ] **Step 4: Commit the red test**

```bash
git add scripts/test-site-render.sh
git commit -m "test: lock book reader reference contract"
```

### Task 2: Add Static Shell Anchors For Mobile Reader Chrome

**Files:**
- Modify: `theme/index.hbs:136-239`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Insert a mobile chapter-bar placeholder directly below the progress line**

Add this block in `theme/index.hbs` after the progress bar and before `#mdbook-content`:

```hbs
<div class="reader-mobile-chapter-bar hidden" aria-hidden="true">
    <button class="reader-mobile-chapter-toggle" type="button" aria-controls="mdbook-sidebar" aria-expanded="false">
        <span class="reader-mobile-chapter-icon">{{fa "regular" "book-open"}}</span>
        <span class="reader-mobile-chapter-kicker"></span>
        <span class="reader-mobile-chapter-title"></span>
        <span class="reader-mobile-chapter-chevron">{{fa "solid" "chevron-down"}}</span>
    </button>
</div>
```

- [ ] **Step 2: Add an article-local anchor that JS can populate with the inline mobile outline**

Insert this node immediately inside `.reader-article`, before `{{{ content }}}`:

```hbs
<div class="reader-mobile-outline-anchor" hidden aria-hidden="true"></div>
```

- [ ] **Step 3: Keep the existing desktop shell intact**

Do **not** change these existing contract points:

- `nav#mdbook-sidebar`
- `img.book-home-icon.book-home-icon-full`
- `img.book-home-icon.book-home-icon-compact`
- `div.toolbar-search-slot`
- `main#mdbook-reader-scroll`
- `aside#mdbook-outline-scroll`

- [ ] **Step 4: Run the render test to move the failure into CSS/JS**

Run:

```bash
npm run test:site
```

Expected: FAIL, but now on missing CSS selectors or JS function names rather than template markers.

- [ ] **Step 5: Commit the shell placeholders**

```bash
git add theme/index.hbs
git commit -m "feat: add mobile reader shell anchors"
```

### Task 3: Re-Token The Reader Shell To Match The Approved Visual System

**Files:**
- Modify: `theme/custom.css:17-224`, `theme/custom.css:549-910`, `theme/custom.css:1925-2023`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Align the top-level reader tokens to the landing-page family**

Update the root token block so the book shell reuses the approved palette instead of the older near-match values:

```css
:root {
  --menu-bar-height: 56px;
  --reader-left-offset: 0px;
  --reader-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --reader-serif: "Literata", Georgia, serif;
  --sidebar-width: 256px;
  --outline-width: 256px;
  --ink: #0b1f33;
  --muted: #526171;
  --paper: #ffffff;
  --panel: #ffffff;
  --line: rgba(11, 31, 51, 0.10);
  --line-strong: rgba(11, 31, 51, 0.18);
  --primary: #3163c2;
  --primary-deep: #264d97;
  --accent: #d88a1d;
  --brand-blue: #3163c2;
  --brand-blue-deep: #264d97;
  --brand-gold: #d9b24a;
  --deep: #0b1f33;
  --soft-blue: #eef2f4;
  --book-bg: #f7f8f9;
  --book-surface: rgba(255, 255, 255, 0.94);
  --book-surface-strong: #ffffff;
}
```

- [ ] **Step 2: Preserve desktop logo sizing exactly as approved**

Keep the header logo scale aligned to the approved mock and current site shell:

```css
.book-home-icon-full {
  width: 138px;
}

.book-home-icon-compact {
  display: none;
  width: 24px;
  height: 24px;
}
```

- [ ] **Step 3: Add mobile-shell styles without weakening desktop**

Append desktop-hidden/mobile-visible rules for the new chrome:

```css
.reader-mobile-chapter-bar {
  display: none;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.98);
}

.reader-mobile-chapter-toggle {
  width: 100%;
  min-height: 48px;
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  border: 0;
  background: transparent;
  color: var(--ink);
  font-family: var(--reader-sans);
  text-align: left;
}

.reader-mobile-outline-card {
  margin: 1rem 0 1.5rem;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(11, 31, 51, 0.10);
  border-radius: 0.9rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.96) 100%);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.045);
}
```

- [ ] **Step 4: Add the narrow-screen breakpoint behavior**

Inside the existing mobile breakpoints, make the shell transform instead of splitting into a separate product:

```css
@media (max-width: 1280px) {
  .reader-outline {
    display: none;
  }

  .reader-mobile-chapter-bar {
    display: block;
  }
}

@media (max-width: 900px) {
  .book-home-icon-full {
    display: none;
  }

  .book-home-icon-compact {
    display: block;
  }
}
```

- [ ] **Step 5: Run the site render test**

Run:

```bash
npm run test:site
```

Expected: FAIL only on the missing JS hooks or runtime shell orchestration.

- [ ] **Step 6: Commit the token and shell CSS**

```bash
git add theme/custom.css
git commit -m "feat: align book reader shell tokens and mobile chrome"
```

### Task 4: Implement Mobile Chapter Context And Inline Outline In JS

**Files:**
- Modify: `theme/custom.js:560-650`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a helper that resolves the active chapter label from the real mdBook sidebar**

Add a helper near `moveOutline()`:

```js
function getActiveSidebarChapterLink() {
  return (
    document.querySelector("#mdbook-sidebar a.active") ||
    document.querySelector("#mdbook-sidebar a.current-header")
  );
}
```

- [ ] **Step 2: Implement `installMobileChapterBar()` using real sidebar state**

Add this function:

```js
function installMobileChapterBar() {
  const bar = document.querySelector(".reader-mobile-chapter-bar");
  const toggle = document.querySelector(".reader-mobile-chapter-toggle");
  const kicker = document.querySelector(".reader-mobile-chapter-kicker");
  const title = document.querySelector(".reader-mobile-chapter-title");
  const sidebarToggle = document.getElementById("mdbook-sidebar-toggle-anchor");
  const activeLink = getActiveSidebarChapterLink();

  if (!bar || !toggle || !kicker || !title || !sidebarToggle || !activeLink) {
    return;
  }

  const normalizedTitle = (activeLink.textContent || "").replace(/\s+/g, " ").trim();
  kicker.textContent = "Chapter";
  title.textContent = normalizedTitle;
  bar.classList.remove("hidden");
  bar.setAttribute("aria-hidden", "false");

  toggle.addEventListener("click", function () {
    sidebarToggle.checked = !sidebarToggle.checked;
    toggle.setAttribute("aria-expanded", sidebarToggle.checked ? "true" : "false");
  });

  toggle.setAttribute("aria-expanded", sidebarToggle.checked ? "true" : "false");
}
```

- [ ] **Step 3: Implement `installInlineOutlineCard()` by cloning the normalized outline into the article**

Add this function:

```js
function installInlineOutlineCard() {
  const anchor = document.querySelector(".reader-mobile-outline-anchor");
  const outline = document.querySelector(".book-outline-body .on-this-page");

  if (!anchor || !outline) {
    return;
  }

  const card = document.createElement("section");
  const label = document.createElement("p");
  const body = outline.cloneNode(true);

  card.className = "reader-mobile-outline-card";
  label.className = "book-outline-label";
  label.textContent = "On This Page";
  card.appendChild(label);
  card.appendChild(body);

  anchor.hidden = false;
  anchor.removeAttribute("aria-hidden");
  anchor.replaceChildren(card);
}
```

- [ ] **Step 4: Wire both functions into the existing startup flow**

Inside the `DOMContentLoaded` branch, after `moveOutline();`, call:

```js
installMobileChapterBar();
installInlineOutlineCard();
```

- [ ] **Step 5: Run the site render test**

Run:

```bash
npm run test:site
```

Expected: PASS if the only missing contract points were the new JS hooks.

- [ ] **Step 6: Commit the reader orchestration**

```bash
git add theme/custom.js
git commit -m "feat: add mobile chapter context and inline outline"
```

### Task 5: Normalize Figures, Tables, And Formulas As One Academic Object Family

**Files:**
- Modify: `theme/custom.css:1347-1888`
- Modify: `theme/custom.js:200-520`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Keep formulas, figures, and tables on the same visual grammar**

Ensure the following families use the same publication treatment:

- formula blocks use white-to-soft-blue paper gradients, thin blue left rule, restrained shadow
- figure cards use rounded white shells, framed media area, subtle divider, blue label, serif caption text
- table shells use the same white shell, subtle border, soft shadow, blue label, serif caption text, and notes below

Do **not** create a second mobile-only object language.

- [ ] **Step 2: Preserve existing formula-rich chapters as the formula acceptance surface**

Do not add invented formula markup to `chapter-01`. Instead verify and, if needed, refine styling against:

- `public/book/chapters/glossary.html`
- `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
- `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`

The formula styling should remain driven by existing source markup such as:

```html
<div class="book-formula api-density-formula" role="img" aria-label="API density equals 141.5 divided by Density at 15 degrees Celsius minus 131.5">
```

and:

```html
<section class="formula-panel formula-panel--r-factor" aria-label="R-factor calculation formulas">
```

- [ ] **Step 3: Keep mobile figures and tables carded instead of flattening them**

Within `@media (max-width: 760px)`, ensure these behaviors remain true:

```css
.figure-card {
  margin: 1.25rem 0 1.5rem;
}

.figure-media {
  padding: 0.75rem;
}

.table-anchor-shell {
  border-radius: 1rem;
}

.table-scroll {
  padding: 0.65rem;
}
```

The mobile rule may collapse grids to one column, but it must not strip card shells, captions, or note treatment.

- [ ] **Step 4: Retain JS wrappers for figure and table semantics**

Keep these existing behaviors intact while adjusting only where needed:

- `annotateFigureCaptions()`
- `annotateTables()`
- `enhanceTable6()`

Do not regress the current wrapper creation paths:

```js
wrapper.className = "figure-card figure-anchor-target";
tableShell.className = "table-anchor-shell";
tableScroll.className = "table-scroll";
caption.className = "table-caption";
```

- [ ] **Step 5: Run the site render test**

Run:

```bash
npm run test:site
```

Expected: PASS, including the existing formula/figure/table assertions already encoded in the script.

- [ ] **Step 6: Commit the knowledge-object normalization**

```bash
git add theme/custom.css theme/custom.js
git commit -m "feat: unify academic content objects across breakpoints"
```

### Task 6: Visual QA The Wide And Narrow Acceptance Surfaces

**Files:**
- No source changes required unless QA finds defects
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Build the site**

Run:

```bash
npm run build:site
```

Expected: PASS and regenerated `public/book/` output.

- [ ] **Step 2: Re-run the render contract**

Run:

```bash
npm run test:site
```

Expected: `Site render checks passed.`

- [ ] **Step 3: Perform manual visual QA on representative pages**

Inspect these generated pages in a local browser or in-app browser:

- `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
- `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
- `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
- `public/book/chapters/glossary.html`

Desktop QA checklist:

- full logo lockup appears at the same restrained scale as the approved wide reference
- sidebar is the only left navigation surface
- right outline reads as a quiet assistive rail
- figure, formula, and table cards feel like one academic family

Mobile QA checklist:

- compact icon replaces the full logo cleanly
- under-header chapter context bar appears
- inline “On This Page” card appears inside article flow
- figures and tables stay carded instead of flattening
- no duplicate or conflicting navigation surfaces appear

- [ ] **Step 4: Commit the final verified state**

```bash
git add theme/index.hbs theme/custom.css theme/custom.js scripts/test-site-render.sh
git commit -m "feat: align book reader to approved desktop and mobile references"
```

## Risks And Decisions To Make During Execution

1. **Mock-vs-source mismatch**
   - Decision: implement the shell and object system from the mock, but keep the live chapter titles and content order from mdBook.
2. **Formula-on-chapter-01 pressure**
   - Decision: do not inject new formula content into `chapter-01` in this plan. Use existing formula-rich chapters as the acceptance surface for formula styling.
3. **Sidebar duplication risk**
   - Decision: keep `nav#mdbook-sidebar` as the only left navigation surface; mobile context bar is a derived summary/toggle, not a second navigation tree.
4. **Mobile flattening risk**
   - Decision: collapse layout, not component identity. Figures and tables keep their desktop family styling on mobile.

## Definition Of Done

- Desktop reader shell matches the approved wide reference in hierarchy, brand continuity, and content-object treatment.
- Mobile reader shell matches the approved narrow reference in structure, logo behavior, and inline navigation strategy.
- Figure, formula, and table components share one academic visual system across breakpoints.
- mdBook remains the only content and navigation engine.
- `npm run test:site` passes.
- No direct edits land in `public/`.

## Suggested New-Thread Execution Prompt

```text
请在 /Users/edison/workspace/peakwalk/scm/gitlab/africa-book 仓库中执行这份方案：

docs/superpowers/plans/2026-06-08-book-reader-reference-alignment.md

要求：
1. 先完整阅读该计划，再开始实施，不要重新写方案。
2. 按计划中的 first principles、MECE workstreams、non-goals 和 file map 执行。
3. 严格保留 mdBook 作为唯一内容与导航引擎，不要编辑 public/。
4. 如果 mock 与真实章节内容冲突，以计划中的 “Source Reality vs. Mock Reality” 为准。
5. 优先执行 shell、responsive chrome、figure/table/formula 对齐，不要把精力转移到 landing page 或其他页面。
6. 执行完成后必须运行计划中的验证命令，至少包括 `npm run test:site`，并汇报通过情况、剩余风险和任何偏离计划的决策。

如果你选择按任务逐项执行，请使用 superpowers:executing-plans；如果你选择分任务派发，请使用 superpowers:subagent-driven-development。
```

Plan complete and saved to `docs/superpowers/plans/2026-06-08-book-reader-reference-alignment.md`.
