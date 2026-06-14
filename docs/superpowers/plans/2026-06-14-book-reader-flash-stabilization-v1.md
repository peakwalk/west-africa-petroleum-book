# Book Reader Flash Stabilization V1 Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the visible layout flash when navigating from the left rail without changing the reader's scroll model in this release.

**Architecture:** Keep the current `#mdbook-reader-scroll` behavior for now, but stop rebuilding sidebar structure after paint. Add a repo-owned post-build step that reads `public/book/toc.html`, injects final `.reader-sidebar-projection` markup into generated chapter pages, and let `theme/custom.js` keep only non-structural reader enhancements. Gate layout-affecting transitions during boot so first paint stays visually stable.

**Tech Stack:** mdBook, Handlebars, vanilla JavaScript, Node.js build scripts, CSS, shell-based render assertions

---

**Scope Decision**

This `v1` plan is intentionally narrower than the broader static-layout roadmap.

Included in `v1`:

- boot-time layout transition gating
- build-time static sidebar injection
- removal of runtime sidebar reprojection
- render-test coverage for the new boot contract

Explicitly deferred from `v1`:

- removing `installInternalScrollerBridge()`
- changing the page back to native document scrolling
- rewriting hash-scroll, progress, or outline logic to a new scroll root

That deferral is the main risk reduction. The biggest regression surface is the scroll model, so `v1` does not touch it.

---

**File Map**

- `theme/index.hbs`: owns the sidebar shell markup and any inline boot-time sidebar logic.
- `theme/custom.js`: owns runtime reader enhancements; in `v1` it must stop rebuilding sidebar structure after paint.
- `theme/custom.css`: owns the layout transition behavior and first-paint motion contract.
- `scripts/build_static_reader_sidebar.mjs`: new build step that converts `public/book/toc.html` into injected final sidebar markup.
- `package.json`: wires the new build step into `build:site`.
- `scripts/preview.sh`: wires the new build step into preview builds.
- `scripts/test-site-render.sh`: owns regression assertions for the new static-sidebar and boot-stability contract.

### Task 1: Stop The Visible Flash First

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a boot-state contract for reader layout**

Add a boot-only class or attribute at template render time so layout transitions can be disabled until the page is ready for user-visible motion.

- [ ] **Step 2: Gate layout-affecting transitions behind that boot-state contract**

Update `theme/custom.css` so geometry-affecting motion such as `padding-inline-start`, `width`, and `margin-inline-start` does not animate during initial page load.

- [ ] **Step 3: Remove one of the two sidebar startup paths before structural refactoring**

Keep only one startup path temporarily so the rail is not visibly rendered twice before the static-sidebar step lands.

- [ ] **Step 4: Lock the contract in render assertions**

Update `scripts/test-site-render.sh` so it fails if the boot-state gate disappears or if unconditional layout transitions are reintroduced.

### Task 2: Inject Static Sidebar Markup At Build Time

**Files:**
- Create: `scripts/build_static_reader_sidebar.mjs`
- Modify: `package.json`
- Modify: `scripts/preview.sh`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Parse the generated mdBook sidebar source**

Read `public/book/toc.html`, extract the `<ol class="chapter">` structure, and group rows into:

- `front-matter`
- `part` sections
- `back-matter`

- [ ] **Step 2: Render final `.reader-sidebar-projection` markup in Node**

Build the same semantic sidebar structure that the runtime projection currently creates, but do it in the build step so the final sidebar exists before the browser paints the page.

- [ ] **Step 3: Inject the rendered sidebar into generated book pages**

Write the final projection markup into:

- `public/book/index.html`
- `public/book/chapters/*.html`

Mark the correct row active per page during injection.

- [ ] **Step 4: Wire the script into both release and preview builds**

Call the new script from:

- `npm run build:site`
- `scripts/preview.sh`

The preview path and release path must stay aligned.

- [ ] **Step 5: Add render assertions for the new static injection**

Update `scripts/test-site-render.sh` to assert that generated chapter pages already contain the final sidebar projection and active-state markers without relying on runtime JS.

### Task 3: Remove Runtime Sidebar Reprojection Only

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/test-site-render.sh`

- [ ] **Step 1: Delete the inline sidebar projection bootstrap from the template**

Remove the inline `bootstrapSidebarProjection()` path from `theme/index.hbs` once static injection is in place.

- [ ] **Step 2: Delete `installSidebarProjection()` and related helpers from `theme/custom.js`**

Remove the runtime code that rebuilds sidebar rows, re-groups parts, or replays sidebar projection after `DOMContentLoaded`.

- [ ] **Step 3: Remove runtime offset restoration that depends on reprojection geometry**

Delete the `sessionStorage`-based sidebar offset restore that mutates the rail after paint if it still depends on computed row geometry from runtime projection.

- [ ] **Step 4: Keep the existing scroll bridge unchanged in `v1`**

Do not modify:

- `installInternalScrollerBridge()`
- `document.scrollingElement` overrides
- hash scrolling bridge
- progress calculations bound to the current scroller

This is an explicit non-change and should be treated as part of the acceptance criteria.

- [ ] **Step 5: Add negative assertions so reprojection does not come back**

Update `scripts/test-site-render.sh` to fail if `theme/custom.js` or `theme/index.hbs` reintroduce the removed sidebar projection bootstrap code.

### Task 4: Verify The Narrow Contract

**Files:**
- Test: `scripts/test-site-render.sh`
- Test: `scripts/test-preview-build.sh`

- [ ] **Step 1: Run the source and generated-output assertions**

Run: `npm run test:site`

Expected: PASS.

- [ ] **Step 2: Run the preview build path**

Run: `sh scripts/test-preview-build.sh`

Expected: PASS.

- [ ] **Step 3: Perform manual navigation smoke checks**

Verify at minimum:

- `foreword.html -> chapter-01`
- `chapter-01 -> chapter-02`
- `chapter-04 -> chapter-05`
- `general-conclusion -> glossary`

Expected:

- no visible page flash
- correct active row at first paint
- no delayed sidebar reprojection
- no regressions in current scroll-linked behavior

---

## Acceptance Criteria

`v1` is complete only if all of the following are true:

1. left-rail navigation no longer produces a visible shift/flash during page-to-page navigation
2. generated chapter HTML contains final sidebar projection markup before client JS runs
3. `theme/index.hbs` no longer contains the inline sidebar projection bootstrap
4. `theme/custom.js` no longer contains runtime sidebar reprojection
5. the existing scroll bridge still works exactly as before
6. `npm run test:site` and `sh scripts/test-preview-build.sh` both pass

---

## Risks And Why This Plan Is Safer

### Reduced Risk 1: No scroll-root migration

This plan does not touch the reader's current scroll model, which avoids the highest-probability regressions in:

- hash navigation
- progress tracking
- outline state sync
- sticky menu behavior

### Reduced Risk 2: One structural change at a time

The only structural migration in `v1` is moving sidebar projection from runtime to build time.

### Remaining Risk: Active-row injection mismatch

Build-time injection must map page paths to the same active state the runtime sidebar previously derived from mdBook.

Mitigation:

- assert active markers in generated HTML
- smoke-test representative front matter, chapter, and back matter pages

---

## Follow-Up After V1

If `v1` removes the flash cleanly, the next plan can separately evaluate whether removing the internal scroll bridge is still worth the regression risk.

That follow-up should be treated as a different change, not silently folded into this one.
