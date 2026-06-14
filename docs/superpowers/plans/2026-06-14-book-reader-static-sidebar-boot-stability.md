# Book Reader Static Sidebar Boot Stability Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (preferred for one worker) or `superpowers:subagent-driven-development` (if splitting build/runtime/QA workstreams) to implement this plan step-by-step.

**Goal:** Remove the visible page flash when navigating from the left rail by moving first-paint reader layout from late JavaScript mutation to build-time HTML/CSS, while preserving mdBook as the single source of navigation truth.

**Architecture:** Keep mdBook generating the canonical TOC and chapter HTML, then add one repo-owned post-build step that reads `public/book/toc.html`, renders the final reader sidebar markup, and injects it into generated chapter pages before preview/test/release verification. Reduce `theme/custom.js` to progressive enhancement only; it must no longer rebuild sidebar structure, remap the scroll root, or change page geometry after first paint.

**Tech Stack:** mdBook, Handlebars theme template, vanilla JavaScript, Node.js build scripts, CSS, shell-based render assertions

---

## Decision Summary

This change should **not** be implemented as a broad "remove all JS" effort.

It should be implemented as a **first-paint contract cleanup**:

1. the sidebar DOM must exist in its final form in generated HTML
2. the browser must keep its native document scroll model
3. runtime JS may enhance behavior, but it must not rebuild navigation structure or rewrite scroll semantics after paint
4. layout transitions must not run during initial boot

That gives the stability benefits of static layout without throwing away useful progressive enhancement.

---

## Why The Current Design Flashes

The current flash comes from three separate responsibilities being mixed into runtime JS:

1. `theme/index.hbs` bootstraps one sidebar projection pass inline
2. `theme/custom.js` runs a second sidebar projection pass on `DOMContentLoaded -> requestAnimationFrame`
3. `theme/custom.js` also bridges `document.scrollingElement`, `window.scrollY`, `window.scrollTo`, and hash scrolling onto `#mdbook-reader-scroll`

This means the page can be painted once using the browser's default document layout, then corrected again after JS finishes mutating the rail and the scroll model.

The visible effect is amplified by layout-affecting transitions in `theme/custom.css`, especially:

- `.reader-main { transition: padding-inline-start 180ms ease; }`
- `.book-progress { transition: width 180ms ease, margin-inline-start 180ms ease; }`

---

## First-Principles End State

After the refactor, the reader should obey these rules:

1. **One navigation tree**
   - mdBook remains the source of truth
   - the generated page contains the final rendered reader sidebar, not a placeholder waiting for JS reconstruction

2. **One scroll root**
   - the browser document remains the scroll root
   - no runtime override of `document.scrollingElement`, `window.scrollY`, `window.scrollTo`, or `window.scrollBy`

3. **Zero first-paint geometry rewrites**
   - no sidebar projection rebuild
   - no late rail scroll correction that changes layout after paint
   - no boot-time transition on layout geometry

4. **JS as enhancement only**
   - search, outline, minor state sync, and optional non-geometric niceties may remain in JS
   - first-paint structure and geometry must not depend on JS

---

## File Map

### Create

- `scripts/build_static_reader_sidebar.mjs`

### Modify

- `package.json`
- `scripts/preview.sh`
- `scripts/test-site-render.sh`
- `theme/index.hbs`
- `theme/custom.js`
- `theme/custom.css`

### Review During Implementation

- `public/book/toc.html` as the canonical generated sidebar source
- `scripts/build_reader_page_meta.mjs` for build-step style and output path conventions
- `scripts/strip_mdbook_onunload.mjs` for existing post-mdBook script placement in the build chain

---

## Implementation Stages

### Stage 0: Stability Guardrail Before Structural Refactor

**Purpose:** Reduce visible flash immediately and create room for the structural change.

**Files:**

- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

**Changes:**

1. add a boot class contract such as `book-layout-booting` on initial HTML
2. suppress geometry transitions while that class is present
3. remove one of the two sidebar projection boot paths before deeper refactoring starts
4. add render assertions that geometry transitions are gated behind the boot-ready class instead of running at first paint

**Acceptance:**

- left-rail navigation no longer performs two visible passes during boot
- `scripts/test-site-render.sh` fails if geometry transitions are reintroduced without boot gating

**Reason for splitting this stage:**

This is the lowest-risk fix for the current symptom and can ship independently if the full static-sidebar migration needs more time.

---

### Stage 1: Build-Time Static Sidebar Injection

**Purpose:** Move sidebar structure creation out of runtime JS and into the build pipeline.

**Files:**

- Create: `scripts/build_static_reader_sidebar.mjs`
- Modify: `package.json`
- Modify: `scripts/preview.sh`
- Modify: `scripts/test-site-render.sh`

**Changes:**

1. read `public/book/toc.html`
2. parse the generated `<ol class="chapter">` into semantic groups:
   - `front-matter`
   - one section per `Part`
   - `back-matter`
3. render final sidebar projection HTML from that parsed structure
4. inject the rendered sidebar markup into:
   - `public/book/index.html`
   - `public/book/chapters/*.html`
5. mark the active row per page during injection, based on the target page path
6. keep `mdbook-sidebar-scrollbox` only as a compatibility fallback if still needed during transition; the final plan target is that the projected markup is the primary visible structure
7. wire the script into both:
   - `npm run build:site`
   - `scripts/preview.sh`

**Recommended implementation detail:**

Do **not** add a new DOM parsing dependency just for this. The generated `toc.html` format is controlled, simple, and already consumed indirectly today. Prefer a repo-local parser in plain Node over bringing in `cheerio` or a client framework.

**Acceptance:**

- generated chapter HTML already contains the final `.reader-sidebar-projection` markup before client JS runs
- active page highlighting is present in generated HTML
- preview and release builds use the same injection step

---

### Stage 2: Remove Runtime Sidebar Reprojection

**Purpose:** Delete the code path that rebuilds sidebar structure after paint.

**Files:**

- Modify: `theme/index.hbs`
- Modify: `theme/custom.js`
- Modify: `scripts/test-site-render.sh`

**Changes:**

1. remove the inline `bootstrapSidebarProjection()` block from `theme/index.hbs`
2. remove `installSidebarProjection()` and its helper functions from `theme/custom.js`
3. remove the mutation-observer behavior that reruns sidebar projection after the sidebar DOM changes
4. remove session-storage offset restoration that depends on runtime reprojected row geometry
5. keep only the minimal sidebar JS that is still justified after static injection

**Important product decision:**

If preserving left-rail internal scroll position across page navigations requires reintroducing late geometry mutation, **drop that feature** for now. Stability is the higher-order requirement. A smaller, earlier, non-geometric restore can be added later only if it does not reintroduce flash.

**Acceptance:**

- `theme/custom.js` no longer contains runtime sidebar projection builders
- `theme/index.hbs` no longer contains inline sidebar projection boot logic
- a generated chapter page can load with correct sidebar structure and active state before enhancement JS runs

---

### Stage 3: Restore Native Document Scrolling

**Purpose:** Remove the second class of first-paint instability: runtime scroll-root remapping.

**Files:**

- Modify: `theme/custom.js`
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

**Changes:**

1. remove `installInternalScrollerBridge()` and all `defineScrollBridgeProperty(...)` overrides
2. stop overriding:
   - `document.scrollingElement`
   - `window.pageYOffset`
   - `window.scrollY`
   - `document.documentElement.scrollTop`
   - `document.body.scrollTop`
   - `window.scrollTo`
   - `window.scrollBy`
3. move reader scroll behavior back to the document scroll root
4. audit every function currently coupled to `#mdbook-reader-scroll`, especially:
   - hash target scrolling
   - progress bar updates
   - outline scroll spy
   - any code that reads or writes `scrollTop`
5. keep `#mdbook-reader-scroll` only as a layout wrapper if necessary; it must no longer be the semantic scroll root

**Acceptance:**

- the page behaves correctly with the browser's native scroll model
- hash links, progress updates, and outline state still work without scroll-root overrides
- `theme/custom.js` no longer contains scroll-bridge property overrides

---

### Stage 4: CSS Simplification Around First Paint

**Purpose:** Ensure CSS does not visually reintroduce a boot-time shift after the structural fixes land.

**Files:**

- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

**Changes:**

1. remove or gate layout-affecting transitions tied to sidebar width / reader left offset
2. keep motion only on user-triggered interactions, not first paint
3. ensure the reader grid, progress bar, and toolbar all resolve from static CSS variables at load time

**Acceptance:**

- no initial layout transition is visible when loading a chapter from the left rail
- hover/focus transitions still work where they are interaction-driven instead of boot-driven

---

## Validation Plan

### Required Commands

1. `npm run build:site`
2. `npm run test:site`
3. `sh scripts/test-preview-build.sh`

### Manual Browser QA

Check at minimum:

1. `foreword.html -> chapter-01`
2. `chapter-01 -> chapter-02`
3. `chapter-04 -> chapter-05`
4. `general-conclusion -> glossary`

For each jump, verify:

1. no visible rail or whole-page flash
2. correct active row on first paint
3. no delayed left-offset correction
4. progress bar and sticky header still behave correctly
5. hash links inside a chapter still land correctly

### Suggested Regression Assertions

Extend `scripts/test-site-render.sh` to assert:

1. generated pages still include `.reader-sidebar-projection`
2. `theme/index.hbs` no longer contains the inline projection bootstrap
3. `theme/custom.js` no longer contains:
   - `installSidebarProjection`
   - `defineScrollBridgeProperty`
   - `document.scrollingElement` overrides
4. `package.json` and `scripts/preview.sh` both call the new static sidebar build step
5. CSS does not apply layout transitions during the booting state

---

## Rollout Strategy

### Preferred Commit Sequence

1. `fix: gate reader layout transitions during boot`
2. `build: inject static reader sidebar from mdbook toc`
3. `refactor: remove runtime sidebar reprojection`
4. `refactor: restore native document scroll model`
5. `test: lock static sidebar boot contract`

### Why multiple commits

This change touches both runtime behavior and the build pipeline. Splitting it into small commits makes it easier to bisect regressions in:

- build output injection
- navigation active-state logic
- scroll behavior
- visual motion contracts

---

## Risks And Mitigations

### Risk 1: mdBook TOC format drift

**Mitigation:** Keep the parser scoped to the exact generated `toc.html` contract used in this repo and lock it with render assertions.

### Risk 2: Losing sidebar scroll-position memory

**Mitigation:** Accept the trade-off initially. Reintroduce only a minimal restore later if it can happen before visible paint and without reprojection.

### Risk 3: Breaking outline/progress behavior when removing the internal scroller

**Mitigation:** Treat scroll-bridge removal as its own stage with explicit browser QA and targeted grep assertions.

### Risk 4: Divergence between `build:site` and preview

**Mitigation:** Add the new sidebar injection script to both `package.json` and `scripts/preview.sh`, then keep `scripts/test-preview-build.sh` green.

---

## Recommendation

Do this in **two delivery phases**, not one:

1. **Symptom stop**: boot transition gate + remove duplicate sidebar boot path
2. **Architectural fix**: static sidebar injection + runtime reprojection removal + native scroll restoration

That sequencing gives a quick user-visible improvement without compromising the first-principles cleanup.
