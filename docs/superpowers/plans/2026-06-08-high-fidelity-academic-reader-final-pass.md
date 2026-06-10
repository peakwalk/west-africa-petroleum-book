# High-Fidelity Academic Reader Final Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the mdBook reader refactor so the live `/book/` experience matches the approved academic-reader reference in layout, hierarchy, typography, and reading flow while preserving mdBook as the sole content and navigation engine.

**Architecture:** Treat the current reader shell as the baseline, not a prototype. Keep `mdBook` responsible for content and navigation, add one derived metadata artifact generated from existing source and git history, and complete the final pass in `theme/index.hbs`, `theme/custom.css`, and `theme/custom.js`. Do not introduce a client framework or a parallel content model.

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, Node build scripts, shell-based render assertions

---

## Current Baseline

The repository already has the following working foundation and this plan must preserve it:

1. Desktop reader shell with fixed header, left navigation rail, center reading column, and right outline rail
2. Mobile chapter context bar and inline `On This Page`
3. Shared figure/table/formula card language
4. Derived `Figures` / `Tables` sections in the right rail
5. `npm run build:site` and `npm run test:site` as the release contract

This plan is a **final-pass refinement**, not a rewrite.

## Design Delta To Close

Compared with the approved design reference, the remaining gaps are:

1. **Opening state still feels generated, not editorial**
   - The current hero is structurally present, but its metadata pills, spacing, and title block do not yet read like the design's scholarly opening spread.
2. **Right rail is correct semantically, but not yet reference-grade**
   - The rail needs stronger section hierarchy, quieter supporting entries, and an active-reading indicator that feels navigational rather than index-like.
3. **Left rail still needs stronger book identity**
   - The current rail has the right pieces, but the information density and section boundaries do not yet feel like a premium monograph reader.
4. **Above-the-fold pacing is still too dependent on raw chapter order**
   - The first figure is visually heavy; the design reference establishes chapter context more decisively before large media dominates the viewport.
5. **Page metadata is too weak for high-fidelity rendering**
   - The design wants a richer chapter meta row. Today we only infer part label and read time from rendered DOM.

## First Principles

1. **Reading before navigation.** Every structural decision must reduce cognitive load for a long-form reader.
2. **Shell fidelity over mock literalism.** Match the design system, hierarchy, and pacing without inventing source content.
3. **mdBook remains the source of truth.** Chapter content and navigation still come from markdown and `SUMMARY.md`.
4. **Derived metadata is allowed.** Generating a metadata artifact from real source and git history is still consistent with mdBook being the only content/navigation engine.
5. **Knowledge objects are first-class scholarly units.** Figures, tables, and formulas must remain visually and behaviorally coherent across breakpoints.

## Non-Goals

- Do not edit `public/` by hand.
- Do not replace mdBook with a SPA, CMS, or client-side router.
- Do not create mock-only content to force chapter 1 to look exactly like the screenshot.
- Do not introduce a second manually curated navigation tree outside `src/SUMMARY.md`.
- Do not weaken the existing `npm run test:site` contract in order to make visual changes easier.

## Source Reality Strategy

To achieve higher fidelity **without** violating the source-reality rule:

1. Derive chapter update dates from git history
2. Derive read time, figure count, table count, and part label from real markdown / rendered output
3. Derive lede text from the first real paragraph of the chapter
4. Optionally allow a small hidden metadata hook inside markdown for pages that need explicit overrides later, but do not require chapter copy rewrites for this pass

## File Map

- Modify: `theme/index.hbs`
  - Final static shell, hero anchor, rail sections, pagination shell
- Modify: `theme/custom.css`
  - Final typography, hero styling, rail hierarchy, object pacing, responsive behavior
- Modify: `theme/custom.js`
  - Hero enrichment, metadata consumption, first-object pacing, rail population
- Modify: `scripts/test-site-render.sh`
  - Final shell + metadata + visual contract assertions
- Modify: `package.json`
  - Wire metadata generation into site build
- Create: `scripts/build_reader_page_meta.mjs`
  - Generate a single book-level metadata JSON from `src/SUMMARY.md`, chapter files, and git history

## Acceptance Surfaces

The implementation must be verified on these pages:

1. `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
2. `public/book/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
3. `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
4. `public/book/chapters/glossary.html`
5. `public/book/index.html`

## Final Visual Contract

### Desktop

- Header keeps the current full `Upstream Atlas` lockup and centered search slot
- Left rail reads like a book navigation system, not a raw document tree
- Hero reads as a chapter opening spread:
  - chapter eyebrow
  - large serif title
  - thin accent rule
  - icon-based metadata row
  - lede text
- Right rail is split into `On This Page`, `Figures`, and `Tables`, with clear density contrast between sections
- First large figure no longer overpowers the hero above the fold

### Mobile

- Compact brand chrome remains
- Chapter context bar persists below header
- Inline `On This Page` appears after the hero, before the first large object
- Figures, tables, and formulas retain the same component identity as desktop

---

### Task 1: Lock The Final Reader Contract In Tests

**Files:**
- Modify: `scripts/test-site-render.sh`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add failing assertions for the final-pass contract**

Add checks such as:

```sh
check_contains package.json 'build:reader-meta'
check_contains scripts/build_reader_page_meta.mjs 'git log -1'
check_contains public/book/reader-page-meta.json 'chapter-01-value-chain-of-the-hydrocarbon-sector.html'
check_contains theme/index.hbs 'class="reader-chapter-hero-anchor"'
check_contains theme/custom.css '.reader-chapter-rule {'
check_contains theme/custom.css '.reader-chapter-meta-item--inline {'
check_contains theme/custom.css '.reader-article--lead-figure-balanced .figure-card:first-of-type {'
check_contains theme/custom.css '.book-outline-active-marker {'
check_contains theme/custom.js 'function applyReaderPageMeta('
check_contains theme/custom.js 'function balanceLeadFigureWeight()'
```

- [ ] **Step 2: Run the site contract and verify it fails**

Run:

```bash
npm run test:site
```

Expected: FAIL on missing `build:reader-meta`, missing `reader-page-meta.json`, or missing hero/rail final-pass selectors.

- [ ] **Step 3: Commit the red contract**

```bash
git add scripts/test-site-render.sh
git commit -m "test: lock final academic reader contract"
```

### Task 2: Add A Derived Reader Metadata Build Artifact

**Files:**
- Create: `scripts/build_reader_page_meta.mjs`
- Modify: `package.json`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Create the metadata generator**

Build a script that:

- parses `src/SUMMARY.md`
- maps markdown chapters to generated html chapter paths
- extracts the first real paragraph from each chapter as the default lede
- runs `git log -1 --format=%cs -- <chapter-path>` for update date
- emits `public/book/reader-page-meta.json`

Use this output shape:

```json
{
  "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html": {
    "eyebrow": "Chapter 1",
    "partLabel": "Part I: General Information on the Oil Industry",
    "updatedAt": "2026-06-08",
    "lede": "As shown in Figure 1, the value chain of the oil sector or the oil industry includes three segments, namely: upstream, midstream and downstream."
  }
}
```

- [ ] **Step 2: Wire the script into site build**

Add a dedicated script and chain it into `build:site`:

```json
{
  "scripts": {
    "build:reader-meta": "node scripts/build_reader_page_meta.mjs",
    "build:site": "... && mdbook build --dest-dir public/book && npm run build:reader-meta"
  }
}
```

- [ ] **Step 3: Verify the artifact exists and has real data**

Run:

```bash
npm run build:site
node -e 'const fs=require("fs");const data=JSON.parse(fs.readFileSync("public/book/reader-page-meta.json","utf8"));if(!data["chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html"]){process.exit(1)}'
```

Expected: PASS and `public/book/reader-page-meta.json` present.

- [ ] **Step 4: Commit the metadata pipeline**

```bash
git add package.json scripts/build_reader_page_meta.mjs
git commit -m "feat: derive reader page metadata from source"
```

### Task 3: Rebuild The Chapter Opening State To Match The Editorial Reference

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Extend the hero markup contract**

Keep the existing anchor, but ensure JS can render this structure:

```html
<section class="reader-chapter-hero">
  <p class="reader-chapter-eyebrow">Chapter 1</p>
  <h1 class="reader-chapter-title">Value Chain of the Hydrocarbon Sector</h1>
  <span class="reader-chapter-rule" aria-hidden="true"></span>
  <div class="reader-chapter-meta reader-chapter-meta--inline">
    <span class="reader-chapter-meta-item reader-chapter-meta-item--inline">...</span>
  </div>
  <p class="reader-chapter-dek">...</p>
</section>
```

- [ ] **Step 2: Consume `reader-page-meta.json` in JS**

Implement:

```js
async function applyReaderPageMeta() {
  const response = await fetch(getPathToRoot() + "reader-page-meta.json");
  const meta = await response.json();
  return meta[getCurrentBookPageKey()] || null;
}
```

Then use that metadata inside `installChapterHero()` instead of relying only on sidebar text and raw paragraph discovery.

- [ ] **Step 3: Replace pill-like meta with editorial inline meta**

Update hero CSS so the chapter opening reads closer to the design:

```css
.reader-chapter-rule {
  width: 2.75rem;
  height: 2px;
  background: var(--brand-gold);
}

.reader-chapter-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.reader-chapter-meta-item--inline {
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}
```

- [ ] **Step 4: Verify the hero on chapter 1 and chapter 2**

Run:

```bash
npm run build:site
npm run test:site
```

Expected: PASS, with generated hero metadata based on real source and metadata JSON.

- [ ] **Step 5: Commit the opening-state refactor**

```bash
git add theme/index.hbs theme/custom.css theme/custom.js
git commit -m "feat: align chapter opening spread to editorial reference"
```

### Task 4: Complete Left And Right Rail Fidelity

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Refine left rail hierarchy**

Tune:

- sidebar intro block spacing
- part-title spacing and muted hierarchy
- active chapter card weight
- bottom utility separation

Add or refine CSS such as:

```css
.book-sidebar-shell .chapter li.part-title {
  margin-top: 1.5rem;
}

.book-sidebar-shell .chapter li a.active::after {
  content: "";
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
}
```

- [ ] **Step 2: Give the right rail a true assistive-navigation rhythm**

Add:

```css
.book-outline-active-marker {
  position: absolute;
  inset-inline-start: -0.45rem;
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background: var(--brand-blue);
}
```

And update JS so the active heading link gets the marker class or wrapper state.

- [ ] **Step 3: Keep figure/table entries quieter than heading entries**

Preserve the existing truncation helper, but ensure:

- headings remain primary
- figure/table references use smaller type
- long captions never dominate the section

- [ ] **Step 4: Verify desktop rail fidelity**

Run:

```bash
npm run test:site
```

Expected: PASS, with left/right rail selectors and contract strings present.

- [ ] **Step 5: Commit rail fidelity**

```bash
git add theme/custom.css theme/custom.js scripts/test-site-render.sh
git commit -m "feat: complete reader rail hierarchy"
```

### Task 5: Balance Knowledge Objects And Above-The-Fold Pacing

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Add a first-object pacing class in JS**

Implement:

```js
function balanceLeadFigureWeight() {
  const article = document.querySelector(".reader-article");
  const firstFigure = article && article.querySelector(".figure-card");
  if (article && firstFigure) {
    article.classList.add("reader-article--lead-figure-balanced");
  }
}
```

- [ ] **Step 2: Reduce the first figure's above-the-fold dominance without moving source order**

Add CSS like:

```css
.reader-article--lead-figure-balanced .figure-card:first-of-type {
  margin-top: 1.25rem;
}

.reader-article--lead-figure-balanced .figure-card:first-of-type .figure-media-item img {
  max-height: min(28rem, 48vw);
}
```

- [ ] **Step 3: Tighten the publication language across figure/table/formula objects**

Ensure consistent:

- card border radius
- caption spacing
- note styling
- object-to-paragraph spacing

- [ ] **Step 4: Verify chapter 1, chapter 4, and glossary**

Run:

```bash
npm run build:site
npm run test:site
```

Expected: PASS, with hero more dominant and object pacing visually calmer.

- [ ] **Step 5: Commit the pacing pass**

```bash
git add theme/custom.css theme/custom.js
git commit -m "feat: balance reader object pacing"
```

### Task 6: Finish Responsive Semantics And Visual QA

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`
- Test: `scripts/test-site-render.sh`

- [ ] **Step 1: Keep mobile hero, chapter bar, and inline outline in the design's order**

Validate and, if needed, enforce:

1. header
2. mobile chapter bar
3. chapter hero
4. inline `On This Page`
5. first large object

- [ ] **Step 2: Run the required verification commands**

Run:

```bash
npm run build:site
npm run test:site
```

Expected: PASS

- [ ] **Step 3: Run manual visual QA on the acceptance surfaces**

Capture at least:

```bash
# Example only; use the repo's normal local preview + browser QA workflow
chapter-01 desktop 1440px
chapter-01 mobile 390px
chapter-02 desktop
chapter-04 formula/table desktop
```

Expected manual checks:

- hero reads as an editorial opening spread
- right rail sections are clearly differentiated
- first figure no longer overpowers the opening state
- mobile still feels like the same reader, not a collapsed docs page

- [ ] **Step 4: Commit the responsive final pass**

```bash
git add theme/custom.css theme/custom.js scripts/test-site-render.sh
git commit -m "feat: finalize high-fidelity academic reader"
```

## Risks To Manage During Execution

1. **Metadata overreach**
   - Do not turn the metadata JSON into a second authoring system. It must remain derived from real source and git history.
2. **Flash-of-unstyled-hero risk**
   - If async metadata fetch causes visible hero shifting, the implementation may need a small inline-loading strategy or synchronous fallback.
3. **Mock literalism**
   - Chapter 1 will still not literally become the mock's chapter. The refactor must improve shell fidelity without falsifying content.
4. **Rail complexity creep**
   - Keep the right rail assistive. Do not convert it into a second sidebar.

## Definition Of Done

The work is done when:

1. `npm run build:site` passes
2. `npm run test:site` passes
3. Chapter openings render from real source + derived metadata, not ad-hoc hardcoded copy
4. Desktop and mobile both present as a premium academic reader
5. The implementation still depends on mdBook for all content and navigation

