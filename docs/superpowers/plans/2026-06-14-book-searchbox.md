# Book SearchBox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `/book/` search as a theme-owned toolbar `SearchBox` that uses local mdBook index data and matches the approved focused-dropdown interaction model.

**Architecture:** Keep `searchindex.js` as the data source, stop loading mdBook `searcher.js`, and move all search state, filtering, rendering, and dismissal behavior into `theme/custom.js`. Use small template and CSS updates in `theme/index.hbs` and `theme/custom.css` to support the clear button, stateful width expansion, and absolute-positioned dropdown, then verify through `npm run test:site`.

**Tech Stack:** mdBook, Handlebars, vanilla JavaScript, CSS, shell-based render assertions

---

**File Map**

- `theme/index.hbs`: owns the search markup and script includes for the book theme.
- `theme/custom.js`: owns the `SearchBox` controller, lazy index loading, filtering, rendering, dismissal, keyboard behavior, and highlight handoff.
- `theme/custom.css`: owns the search shell width-state styling and dropdown/result presentation.
- `scripts/test-site-render.sh`: owns regression assertions for theme source and generated `/public/book` output.

### Task 1: Update Search Markup And Assertions

**Files:**
- Modify: `theme/index.hbs`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Replace the default mdBook search hook points in the template**

Update the search block in `theme/index.hbs` so the form keeps the existing ids but adds a clear button and no longer loads `searcher.js`.

- [ ] **Step 2: Assert the new template markers and script contract**

Update `scripts/test-site-render.sh` to check for the clear button, focused dropdown wiring markers, and the absence of `searcher.js` in the source template.

- [ ] **Step 3: Run the render test to confirm the new assertions fail before implementation is complete**

Run: `npm run test:site`

Expected: a failure on newly asserted search markup or script markers before the JS/CSS implementation lands.

### Task 2: Implement The SearchBox Controller

**Files:**
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a theme-owned search state controller**

Implement local `query`, `focused`, `results`, and `activeIndex` state; lazy-load `searchindex.js`; filter against `title`, `body`, and `breadcrumbs`; and render the dropdown and empty state.

- [ ] **Step 2: Add interaction handling**

Implement focus entry, outside-click `mousedown` dismissal, clear-button `mousedown` prevention, clear/reset behavior, result navigation, `/` and `s` shortcuts, and optional Arrow/Enter/Escape keyboard handling.

- [ ] **Step 3: Preserve highlight-on-navigation behavior**

Append `highlight=<query>` to result links and apply `Mark` to destination content on load when that parameter exists.

### Task 3: Add CSS Support And Verify

**Files:**
- Modify: `theme/custom.css`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add focused-width and dropdown styles**

Style the toolbar search slot so a JS-controlled focus class expands the input slightly, the clear button sits inside the field, and the results panel is an absolute dropdown below the input.

- [ ] **Step 2: Style result rows and empty state just enough to support the interaction**

Add selectors for result rows, active result state, icon chip, excerpt, and empty-state container without redesigning the broader reader shell.

- [ ] **Step 3: Run the full site render assertions**

Run: `npm run test:site`

Expected: PASS.
