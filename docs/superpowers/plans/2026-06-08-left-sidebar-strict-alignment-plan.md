# Left Sidebar Strict Alignment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (preferred for one worker) or `superpowers:subagent-driven-development` (if splitting DOM/CSS/QA workstreams) to implement this plan step-by-step.

**Goal:** Bring the desktop left navigation rail into strict alignment with the approved academic-reader reference so it reads as a premium monograph navigation system, not a styled mdBook table of contents, while keeping mdBook as the sole content and navigation engine.

**Architecture:** Keep `theme/index.hbs` as the only shell template, continue to source navigation from mdBook / `SUMMARY.md`, and add a small **sidebar projection layer** in `theme/custom.js` that transforms mdBook's injected TOC DOM into design-aligned left-rail sections and row components. Do not introduce a second navigation tree, client framework, or manual content model.

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions

---

## Problem Statement

The current left rail has the right high-level pieces:

1. book identity block
2. chapter navigation
3. bottom reference utilities

But it still does **not** match the reference at the level that matters for perceived quality:

1. the rail feels like three unrelated blocks instead of one unified book-navigation instrument
2. the chapter tree is still too literally the mdBook TOC
3. row anatomy does not match the numbered, editorial navigation cards in the reference
4. the footer utility area still reads like plain links instead of reference surfaces
5. the fixed top/middle/bottom regions use hard-coded geometry instead of deriving layout from real content height

---

## First Principles

1. **The left rail is an orientation system, not a raw index.**
   - It exists to answer: where am I, what chapter cluster am I in, and what adjacent reference surfaces can I jump to?
2. **One rail, one grid.**
   - Intro, navigation, and utility footer must share one horizontal rhythm and one section boundary system.
3. **Navigation rows are components, not text links.**
   - A chapter row needs explicit slots for ordinal, label, active state, and multiline wrapping.
4. **Fixed regions must be derived, not guessed.**
   - If top and bottom regions are sticky, the scrollable middle must size itself from measured heights, not magic numbers.
5. **mdBook remains the source of truth.**
   - The rail may be transformed, regrouped, or annotated, but the data still comes from mdBook output and `SUMMARY.md`.

---

## MECE Root Cause Analysis

### 1. Geometry Contract Mismatch

The left rail does not share one stable geometric contract from top to bottom.

- `book-sidebar-intro`, the scrollbox, and `book-sidebar-utilities` use different optical padding rules
- the scrollable middle still relies on hard-coded offsets:
  - `top: 6.35rem`
  - `bottom: 10.2rem`
- those values were tuned against a previous type scale and are now detached from the actual intro/footer content heights

**Effect:** even when text sizes improve, the rail still feels slightly compressed, over-gapped, or visually inconsistent.

### 2. Navigation Structure Projection Mismatch

The current left rail is still styling mdBook's flat TOC too directly.

Evidence:

- mdBook injects a flat `<ol class="chapter">` via `public/book/toc-*.js`
- `Front Matter`, `Part I`, `Part II`, `Part III`, and `Back Matter` arrive as raw `li.part-title` nodes
- chapter links arrive as plain anchors inside `.chapter-link-wrapper`

The reference does **not** present this raw structure directly. It projects it into:

1. a top “Front Matter” navigation group
2. distinct part blocks with stronger section separation
3. numbered chapter rows with editorial hierarchy
4. a visually separate utility footer

**Effect:** current styling can improve typography, but it cannot reach strict fidelity while the DOM still behaves like a flat document list.

### 3. Row Component Anatomy Mismatch

The design expects each navigable chapter item to behave like a structured row, but the current implementation styles a generic anchor.

Current constraint:

- `.book-sidebar-shell .chapter li a` is one padded block with inline text

Reference expectation:

1. dedicated ordinal lane
2. dedicated text lane
3. predictable multiline wrapping width
4. active blue card with end-dot aligned to the card, not to raw text
5. distinct handling for non-chapter items such as `Cover`, `Glossary`, and `Bibliographical References`

**Effect:** the rail lacks the crisp “number + title” hierarchy that makes the reference feel editorial instead of utilitarian.

### 4. Section Chrome Mismatch

The section-level affordances still do not match the reference.

- the top “Front Matter” region is not rendered as an explicit rail group header with its own chrome
- part headers are still low-information raw `part-title` rows
- bottom `Reference Surfaces` links are plain text rows; the reference uses richer utility treatment
- the current footer lacks icon slots and the stronger “surface” semantics seen in the reference

**Effect:** even if typography is corrected, the rail still reads as “styled TOC + extra links”, not as a designed navigation object.

### 5. Interaction And State Mismatch

The state model is underpowered relative to the design.

- current active-state handling focuses on `a.active` and `a.current-header`
- there is no explicit concept of “current part block”, “front matter group”, or “utility surface state”
- the current implementation does not derive sticky-region measurements or section expansion state from actual DOM conditions

**Effect:** the rail is visually close in some places, but behaviorally loose and therefore not truly aligned.

### 6. Verification Gap

Current tests cover:

1. sidebar presence
2. width tokens
3. typography tokens
4. absence of removed artifacts

They do **not** yet lock:

1. projected sidebar section wrappers
2. numbered chapter row anatomy
3. utility-link icon contract
4. measured-height layout variables
5. current-page state on chapter pages vs. back-matter pages

**Effect:** the rail can regress back toward raw mdBook styling without failing CI.

---

## Solution Strategy

### Overview

Do **not** replace mdBook navigation. Instead, add a **left-rail projection layer** that consumes mdBook's injected TOC DOM and re-renders it into a stricter navigation structure.

This keeps source truth in mdBook while allowing design-fidelity at the shell layer.

### Core Design Decisions

1. **Measure, don't guess**
   - Replace hard-coded scrollbox `top` / `bottom` values with CSS custom properties set from observed intro/footer heights.
2. **Project navigation into explicit groups**
   - Convert the flat mdBook TOC into:
     - `front-matter`
     - one block per `Part`
     - `back-matter`
3. **Split chapter rows into slots**
   - Parse `Chapter N: Title` into:
     - chapter number slot
     - title slot
4. **Differentiate row classes by semantic type**
   - chapter rows
   - front/back matter rows
   - utility footer rows
5. **Keep the footer utilities static in template, but upgrade their component treatment**
   - add icon slots and consistent row anatomy
6. **Do not reintroduce mock-only `Download PDF`**
   - unless product explicitly restores a real canonical PDF contract in a separate task

---

## MECE Workstreams

### Workstream 1. Sidebar Shell Geometry

Own the physical layout of the rail.

- derive `--sidebar-intro-height`
- derive `--sidebar-utilities-height`
- compute scrollbox inset from those variables
- unify left/right padding and section boundary rhythm

### Workstream 2. Navigation Projection Layer

Own the transformation from raw mdBook TOC to design-aligned groups.

- read mdBook-injected `.chapter` list
- group entries into front matter / parts / back matter
- rebuild section wrappers inside the scrollbox
- preserve original hrefs, active state, and mdBook source truth

### Workstream 3. Row Component System

Own chapter-row anatomy and section-header anatomy.

- dedicated number slot for `Chapter N`
- multiline title slot
- active state card + end-dot
- separate styling for non-numbered entries

### Workstream 4. Utility Surfaces Footer

Own the bottom reference-surface treatment.

- icon slot per utility row
- denser but still premium footer layout
- current-page highlighting where relevant

### Workstream 5. Verification And Visual QA

Own test coverage and acceptance criteria.

- extend `scripts/test-site-render.sh`
- verify generated output on representative pages
- run browser QA on left-rail alignment, not just CSS grep

---

## Non-Goals

1. Do not edit `public/` by hand.
2. Do not replace mdBook TOC generation.
3. Do not introduce a second, manually curated navigation JSON.
4. Do not broaden this task into header, hero, or right-rail redesign.
5. Do not restore a fake `Download PDF` CTA.

---

## File Map

- Modify: `theme/index.hbs`
  - optional wrapper hooks for projected sidebar content and utility icons
- Modify: `theme/custom.css`
  - left-rail geometry, section wrappers, row anatomy, utility row system
- Modify: `theme/custom.js`
  - sidebar projection, measurement, current-state sync
- Modify: `scripts/test-site-render.sh`
  - contracts for projected DOM, CSS hooks, and utility/footer state

---

## Acceptance Surfaces

Verify the left rail on these generated pages:

1. `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
   - active chapter row in `Part I`
2. `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
   - active chapter row in `Part II`
3. `public/book/chapters/glossary.html`
   - back-matter active state
4. `public/book/chapters/list-of-figures.html`
   - utility-surface page state

---

## Implementation Plan

### Task 1. Lock The Left-Rail Contract In Tests

**Files:**
- Modify: `scripts/test-site-render.sh`

- [ ] Add failing assertions for the projected sidebar structure, for example:
  - `.reader-sidebar-section`
  - `.reader-sidebar-section-header`
  - `.reader-sidebar-section-body`
  - `.reader-sidebar-row`
  - `.reader-sidebar-row-index`
  - `.reader-sidebar-row-title`
  - `.book-sidebar-utility-link-icon`
  - `--sidebar-intro-height`
  - `--sidebar-utilities-height`
- [ ] Add generated-output checks for active-state classes on representative pages.
- [ ] Run `npm run test:site` and verify failure occurs on the new left-rail contract.

### Task 2. Replace Magic Sidebar Offsets With Measured Geometry

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`

- [ ] Add CSS variables for intro/footer measured heights.
- [ ] Replace hard-coded scrollbox `top` / `bottom` with those variables.
- [ ] Use `ResizeObserver` in `theme/custom.js` to keep those variables in sync.
- [ ] Preserve existing mobile behavior.

### Task 3. Build A Sidebar Projection Layer From mdBook TOC

**Files:**
- Modify: `theme/custom.js`

- [ ] Read the injected `.chapter` tree after `mdbook-sidebar-scrollbox` populates.
- [ ] Parse `part-title` boundaries.
- [ ] Group entries into:
  - front matter
  - one section per part
  - back matter
- [ ] Re-render the groups into explicit wrappers while preserving the original link targets and active state.
- [ ] Ensure the projection re-runs safely after sidebar mutations.

### Task 4. Rebuild Chapter Rows As Structured Components

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`

- [ ] Parse `Chapter N: Title` into index + title slots.
- [ ] Render numbered rows as two-column navigation components.
- [ ] Render non-numbered entries with a simpler row variant.
- [ ] Tune active, hover, current-part, and multiline wrapping behavior to match the reference.

### Task 5. Upgrade Front Matter / Part Headers / Back Matter Chrome

**Files:**
- Modify: `theme/custom.css`
- Modify: `theme/custom.js`

- [ ] Give the `Front Matter` section an explicit section-header treatment.
- [ ] Give each part block stronger separation and accent treatment.
- [ ] Keep `Back Matter` visually quieter but still grouped.
- [ ] Ensure spacing between groups matches the reference rhythm.

### Task 6. Upgrade Reference Surfaces Footer

**Files:**
- Modify: `theme/index.hbs`
- Modify: `theme/custom.css`

- [ ] Add icon slots to the footer utility links.
- [ ] Align utility rows to the same rail grid as the chapter rows.
- [ ] Add current-page state for utility pages like `Glossary` and `List of Figures`.
- [ ] Do not add `Download PDF`.

### Task 7. Verification

**Files:**
- Modify: `scripts/test-site-render.sh`

- [ ] Run `npm run build:site`
- [ ] Run `npm run test:site`
- [ ] Do browser QA on the four acceptance surfaces above.
- [ ] Validate:
  - intro/footer do not overlap the scrollbox
  - current section is visually obvious
  - row numbers and titles align consistently
  - utility footer feels like reference surfaces, not stray links

---

## Expected End State

When this plan is complete, the left rail should:

1. feel like a single designed navigation instrument
2. preserve mdBook as the only navigation engine
3. visually match the reference in section rhythm, row anatomy, and footer treatment
4. stop depending on fragile hard-coded offsets
5. be guarded by explicit tests against regression

