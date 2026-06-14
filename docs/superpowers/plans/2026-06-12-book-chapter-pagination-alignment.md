# Book Chapter Pagination Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the book reader's chapter pagination to the approved wide and thin designs without changing mdBook's chapter data flow or template structure.

**Architecture:** Keep `theme/index.hbs` unchanged, rewrite the pagination layout model in `theme/custom.css`, gate the runtime equal-height logic in `theme/custom.js` to wide screens only, and update the shell-based regression script to encode the new layout contract before changing production code.

**Tech Stack:** mdBook theme templates, CSS, vanilla JavaScript, shell-based regression checks

---

### Task 1: Encode the new pagination contract in tests first

**Files:**
- Modify: `scripts/test-book-pagination-render.sh`
- Reference: `docs/superpowers/specs/2026-06-12-book-chapter-pagination-alignment-design.zh_CN.md`

- [ ] **Step 1: Write the failing regression assertions**

Add assertions for:

```sh
width: min(100%, var(--reader-article-body-width));
display: grid;
grid-template-columns: repeat(2, minmax(0, 1fr));
min-height: 92px;
padding: 12px 16px;
width: 44px;
height: 44px;
font-size: 16px;
font-size: 10px;
gap: 12px;
padding: 12px 14px;
justify-items: center;
text-align: center;
```

- [ ] **Step 2: Run the pagination script to verify it fails**

Run: `sh scripts/test-book-pagination-render.sh`

Expected: FAIL on the new wide/thin pagination expectations because the implementation still uses the old `224px`/`80px` layout model.

### Task 2: Rebuild the wide pagination layout model

**Files:**
- Modify: `theme/custom.css:2068-2259`
- Reference: `theme/index.hbs:569-600`

- [ ] **Step 1: Replace the wide container layout**

Update the container from flex distribution to equal-width grid:

```css
.chapter-pagination {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: 12px;
  width: min(100%, var(--reader-article-body-width));
  max-width: none;
  margin-top: 24px;
  margin-inline: auto;
}
```

- [ ] **Step 2: Replace the wide card sizing tokens**

Update the cards to fill the grid instead of capping at `224px`:

```css
.chapter-nav-card {
  width: 100%;
  max-width: none;
  min-height: 92px;
  height: auto;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
}
```

- [ ] **Step 3: Update wide badge, text, and ornament sizing**

Set the wide typography and ornament tokens:

```css
.chapter-nav-badge { width: 44px; height: 44px; }
.chapter-nav-arrow { font-size: 24px; }
.chapter-nav-card[data-chapter-badge-type="number"] .chapter-nav-arrow { font-size: 20px; }
.chapter-nav-label { font-size: 11px; line-height: 13px; letter-spacing: 0.08em; }
.chapter-nav-title { font-size: 16px; line-height: 1.08; }
.chapter-nav-dek { font-size: 10px; line-height: 1.3; max-width: none; }
.chapter-nav-card::after { width: 68px; height: 60px; opacity: 0.12; }
```

- [ ] **Step 4: Run the pagination script to verify the wide rules pass and the thin rules still fail**

Run: `sh scripts/test-book-pagination-render.sh`

Expected: FAIL only on thin-screen expectations or JS expectations that still reflect the old behavior.

### Task 3: Rebuild the thin pagination layout model

**Files:**
- Modify: `theme/custom.css:3998-4086`

- [ ] **Step 1: Update the stacked container spacing**

Replace the old narrow gap and top spacing behavior:

```css
.chapter-pagination {
  gap: 12px;
  margin-top: 16px;
}
```

- [ ] **Step 2: Replace the thin card tokens**

Use the new stacked-card dimensions:

```css
.chapter-nav-card {
  width: 100%;
  height: auto;
  min-height: 92px;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
}
```

- [ ] **Step 3: Rebuild the thin previous and next grid templates**

Apply asymmetric three-column layouts:

```css
.chapter-nav-previous {
  grid-template-columns: 44px minmax(0, 1fr) 72px;
}

.chapter-nav-next {
  grid-template-columns: 72px minmax(0, 1fr) 44px;
}
```

- [ ] **Step 4: Update thin text alignment, badge sizing, and ornament sizing**

Apply the thin typography and centered next-card rules:

```css
.chapter-nav-badge { width: 44px; height: 44px; }
.chapter-nav-arrow { font-size: 24px; }
.chapter-nav-card[data-chapter-badge-type="number"] .chapter-nav-arrow { font-size: 20px; }
.chapter-nav-label { font-size: 12px; line-height: 14px; }
.chapter-nav-title { font-size: 16px; line-height: 17px; }
.chapter-nav-dek { font-size: 10px; line-height: 13px; }
.chapter-nav-next .chapter-nav-body { justify-items: center; text-align: center; }
.chapter-nav-next .chapter-nav-label { justify-self: center; }
.chapter-nav-card::after { width: 72px; height: 60px; bottom: 8px; opacity: 0.13; }
```

- [ ] **Step 5: Run the pagination script to verify only JS-related expectations remain**

Run: `sh scripts/test-book-pagination-render.sh`

Expected: PASS on CSS layout checks, with any remaining failure pointing at the runtime equal-height behavior if it is still global.

### Task 4: Restrict runtime equal-height behavior to wide screens only

**Files:**
- Modify: `theme/custom.js:2046-2088`

- [ ] **Step 1: Add a wide-screen gate to the equal-height sync**

Use a `window.matchMedia("(min-width: 761px)")` guard and clear inline heights on thin screens:

```js
const widePaginationMediaQuery = window.matchMedia("(min-width: 761px)");

if (!widePaginationMediaQuery.matches) {
  cards.forEach(function (card) {
    card.style.height = "";
  });
  return;
}
```

- [ ] **Step 2: Re-run the pagination script to verify it passes**

Run: `sh scripts/test-book-pagination-render.sh`

Expected: PASS

### Task 5: Run full verification

**Files:**
- Verify: `theme/custom.css`
- Verify: `theme/custom.js`
- Verify: `scripts/test-book-pagination-render.sh`

- [ ] **Step 1: Run the full site render check**

Run: `npm run test:site`

Expected: PASS with `Site render checks passed.`

- [ ] **Step 2: Review the final diff for scope control**

Run: `git diff -- theme/custom.css theme/custom.js scripts/test-book-pagination-render.sh docs/superpowers/plans/2026-06-12-book-chapter-pagination-alignment.md`

Expected: Only pagination styling, pagination JS behavior, regression checks, and the new plan document are included.
