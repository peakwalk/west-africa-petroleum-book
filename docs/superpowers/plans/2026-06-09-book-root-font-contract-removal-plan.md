# /book Root Font Contract Removal Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the implicit mdBook `:root { font-size: 62.5%; }` dependency from the `/book` reader surface, replace it with a repository-owned root font contract, and re-author `/book` typography tokens so reader chrome stops depending on a hidden 10px rem baseline.

**Architecture:** Keep mdBook as the content and navigation engine. Do not edit generated `public/` assets. Override the mdBook root font contract inside `theme/custom.css`, then migrate `/book` chrome typography from “10px-root-authored rem values” to an explicit repo-owned scale based on a standard browser root. Update tests so CI protects the new contract instead of the old mdBook default.

**Tech Stack:** mdBook, Handlebars theme template, CSS, vanilla JavaScript, shell-based render assertions

---

## Problem Statement

The current `/book` reader surface still inherits mdBook’s generated default:

- `public/book/css/general-*.css` defines `:root { font-size: 62.5%; }`
- `theme/custom.css` is authored on top of that hidden assumption
- `scripts/test-site-render.sh` currently protects that assumption as a correctness contract

This causes two classes of failure:

1. the typography contract is **implicit and external**
2. the left rail, outline, and related reader chrome are authored against a **10px rem baseline** that is easy to forget and easy to misreason about

The observed symptom is not only “left sidebar text feels too small.” The deeper problem is that the `/book` reader chrome is being sized against a third-party default rather than a repository-owned design contract.

---

## Current Facts

1. The current generated mdBook root font rule is **`62.5%`**, not `65.8%`.
2. The source of that rule is mdBook’s generated `general-*.css`, not `theme/custom.css`.
3. `theme/custom.css` is loaded after `general-*.css`, so the repo already has a stable override point.
4. Current tests lock the old behavior:
   - `scripts/test-site-render.sh` asserts the generated `general-*.css` keeps `62.5%`
   - many left-rail contracts are expressed in rem values that only make physical sense under the 10px-root assumption

---

## First Principles

1. **Typography contracts must be local and explicit.**
   - A repository should not depend on a generated third-party default for its primary sizing model.

2. **Navigation readability outranks density.**
   - The left rail exists to orient, not to maximize line count. If the text is hard to read, the navigation is failing its primary job.

3. **Root font size is infrastructure, not styling trivia.**
   - Changing it affects every rem-authored surface in `/book`. It must be treated as a platform migration, not a one-line tweak.

4. **Component tokens should encode intended physical scale, not hidden math.**
   - `1.06rem` only means something useful if the root contract is explicit and owned.

5. **Tests must protect the repo-owned contract, not the implementation detail of a generator.**
   - CI should fail when our explicit root override disappears, not when mdBook stops shipping its old default.

6. **Landing and `/book` are separate typography systems.**
   - This migration concerns `/book` only. Landing page contracts must remain untouched.

---

## MECE Root Cause Analysis

### 1. Hidden Contract Root Cause

The `/book` root font size is currently inherited from generated mdBook CSS rather than explicitly declared in repo-owned theme code.

**Effect:** engineers reason about `/book` typography from incomplete information and keep rediscovering the 10px-root assumption after the fact.

### 2. Token Authoring Root Cause

Reader chrome tokens were authored under `1rem = 10px`, especially in:

- left rail intro
- part/front/back matter headers
- row title/index anatomy
- outline labels
- some toolbar and reader chrome surfaces

**Effect:** once the hidden root assumption is forgotten, the authored rem numbers look deceptively normal while rendering physically smaller than expected.

### 3. Test Lock-In Root Cause

`scripts/test-site-render.sh` currently asserts that generated mdBook `general-*.css` must keep `62.5%`.

**Effect:** CI protects the old implicit contract, making it harder to migrate away from it safely.

### 4. Mixed-Scale Root Cause

The `/book` CSS mixes:

- px-based dimensions
- rem-based typography authored for a 10px root
- semantic intentions that are not encoded as named tokens

**Effect:** the system is difficult to reason about and difficult to audit after a root-size change.

### 5. Verification Gap Root Cause

Current checks mostly grep source and generated output. They do not establish a clear computed-style contract for the main `/book` navigation hierarchy after a root baseline change.

**Effect:** regressions can survive if the code “looks plausible” but the rendered optical scale is still off.

---

## Recommended Decision

### Decision

Adopt a repo-owned `/book` root font contract of:

```css
:root {
  font-size: 100%;
}
```

inside `theme/custom.css`, and treat this as the new source of truth for `/book`.

### Why this is the right decision

1. it removes dependence on mdBook’s generated default
2. it restores standard browser expectations for rem math
3. it keeps accessibility behavior aligned with the user’s default browser font size
4. it gives the repo a stable, explicit contract that future contributors can discover directly in source

### What this decision is not

- It is **not** “just make everything 1.6x larger.”
- It is **not** “preserve all existing physical sizes by reverse-converting every old rem.”
- It is **not** a landing-page typography migration.

The migration must intentionally re-author `/book` chrome typography rather than blindly preserving or blindly amplifying every old value.

---

## Alternative Approaches Considered

### Option A. Keep mdBook `62.5%` and just enlarge left-rail fonts

**Rejected**

This fixes one symptom but preserves the hidden root contract that caused the confusion in the first place.

### Option B. Override `/book` root to `100%` and keep all existing rem values

**Rejected**

This would enlarge every rem-authored `/book` surface by ~1.6x and almost certainly break toolbar, outline, spacing, and surrounding reader chrome.

### Option C. Override `/book` root to `100%` and re-author affected `/book` chrome tokens

**Recommended**

This is the only approach that fixes the underlying contract problem while keeping optical control over the resulting reader UI.

---

## Scope

### In Scope

- `/book` root font contract
- left rail typography and row anatomy
- reader outline typography
- reader toolbar / chapter bar typography if affected by rem-based scaling
- `/book`-specific tests that currently protect the `62.5%` contract

### Out of Scope

- landing page root font size
- generated `public/` asset edits
- mdBook content structure changes in `SUMMARY.md`
- right-rail IA redesign
- chapter content rewriting

---

## File Map

- Modify: `theme/custom.css`
  - add repo-owned `/book` root font contract
  - re-author reader chrome type scale and any dependent spacing tokens

- Modify: `scripts/test-site-render.sh`
  - remove the generated `62.5%` expectation
  - add assertions for the explicit root override in `theme/custom.css`
  - update left-rail / outline typography expectations to the new scale

- Potentially modify: `theme/custom.js`
  - only if runtime QA requires computed-style instrumentation or if any geometry reveal logic needs tuning after the type-scale change

- No changes expected: `book.toml`
  - the load order already supports overriding mdBook CSS via `additional-css`

---

## Acceptance Surfaces

Verify typography after the migration on:

1. `public/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html`
   - active chapter row in `Part I`

2. `public/book/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
   - active chapter row in `Part II`

3. `public/book/chapters/glossary.html`
   - back matter row readability with icon slot

4. `public/book/chapters/bibliographical-references.html`
   - back matter row readability with icon slot

5. `public/book/index.html`
   - root CSS load order and generated asset references

---

## Migration Strategy

### Phase 1. Replace the hidden root contract

Introduce an explicit `/book` root override in `theme/custom.css`.

**Outcome:** the repo, not mdBook generated CSS, owns the root font-size contract.

### Phase 2. Audit all rem-authored reader chrome

Group rem-based reader chrome into MECE buckets:

1. left rail
2. outline
3. toolbar / mobile chapter bar
4. pagination / shell chrome
5. content-adjacent widgets that use chrome typography rather than article typography

**Outcome:** no migration is done by guesswork.

### Phase 3. Re-author typography by intended physical outcome

Do not reverse-convert old values mechanically. Instead, define the intended physical reading scale per surface.

**Recommended target bands:**

- left-rail book title: `1.125rem` to `1.25rem`
- left-rail section titles: `0.9375rem` to `1rem`
- chapter row titles: `1rem` to `1.0625rem`
- chapter row indices: `0.75rem` to `0.8125rem`
- outline labels: `0.9375rem` to `1rem`

**Outcome:** legibility is restored intentionally, not accidentally.

### Phase 4. Move tests to the new contract

Tests must assert:

1. `theme/custom.css` explicitly declares the `/book` root font contract
2. generated `general-*.css` may still contain `62.5%`, but that is no longer the protected source of truth
3. key typography surfaces use the new repo-owned scale

**Outcome:** future regressions fail at the right abstraction layer.

### Phase 5. Browser QA

Validate the real rendered result, not just static CSS presence.

Check:

- left-rail optical size
- chapter row scanability
- part header contrast and readability
- back matter icon row alignment
- no geometry regressions in sticky/scroll behavior

---

## Implementation Plan

### Task 1. Lock the new root-contract migration in tests

**Files:**
- Modify: `scripts/test-site-render.sh`

- [ ] Remove the assertion that requires generated mdBook `general-*.css` to keep `62.5%`.
- [ ] Add a failing assertion that `theme/custom.css` contains a repo-owned `:root { font-size: 100%; }`.
- [ ] Add a failing assertion that no test message refers to a `/book 62.5% root contract`.
- [ ] Run: `npm run test:site`
- [ ] Expected: FAIL because `theme/custom.css` does not yet override the root font size.

### Task 2. Introduce the explicit `/book` root font contract

**Files:**
- Modify: `theme/custom.css`

- [ ] Add a root override near the top of the file:
  ```css
  :root {
    font-size: 100%;
  }
  ```
- [ ] Keep this override close to the existing theme tokens so future readers can discover it immediately.
- [ ] Run: `npm run test:site`
- [ ] Expected: FAIL on reader chrome token expectations, not on the missing root contract.

### Task 3. Audit left-rail token values under the new root

**Files:**
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

- [ ] Re-author the left-rail intro hierarchy:
  - `.book-sidebar-kicker`
  - `.book-sidebar-book-title`
- [ ] Re-author section header hierarchy:
  - `.reader-sidebar-section-kicker`
  - `.reader-sidebar-section-title`
  - `.reader-sidebar-section--part .reader-sidebar-section-kicker`
  - `.reader-sidebar-section--part .reader-sidebar-section-title`
- [ ] Re-author row hierarchy:
  - `.reader-sidebar-row-index`
  - `.reader-sidebar-row-title`
  - `.reader-sidebar-row--reference .reader-sidebar-row-title`
- [ ] Update the test contract with the new expected values.
- [ ] Run: `npm run test:site`
- [ ] Expected: PASS for left-rail contract assertions.

### Task 4. Audit reader-outline and toolbar typography

**Files:**
- Modify: `theme/custom.css`
- Modify: `scripts/test-site-render.sh`

- [ ] Inspect rem-authored outline and toolbar text tokens and decide whether each one should:
  - stay in rem at the new root
  - move to a different rem value
  - remain px if it is truly a fixed chrome dimension rather than text scale
- [ ] Update test expectations where those tokens change.
- [ ] Run: `npm run test:site`
- [ ] Expected: PASS with no old-root assumptions remaining.

### Task 5. Audit content-adjacent `/book` widgets affected by rem scaling

**Files:**
- Modify as needed: `theme/custom.css`
- Modify as needed: `scripts/test-site-render.sh`

- [ ] Review rem-authored widgets likely influenced by the root change:
  - chapter pagination cards
  - formula and figure chrome labels
  - mobile reader chapter bar
  - any sidebar-adjacent helper text
- [ ] Re-author only the surfaces whose rendered size clearly regresses.
- [ ] Keep article body typography out of scope unless a regression is directly caused by the root override.
- [ ] Run: `npm run test:site`
- [ ] Expected: PASS after each adjusted surface.

### Task 6. Run full build verification

**Files:**
- No source edits required beyond prior tasks

- [ ] Run: `npm run build:site`
- [ ] Expected: PASS
- [ ] Confirm the generated `public/book/index.html` still loads `theme/custom-*.css` after `general-*.css`.

### Task 7. Browser QA on acceptance surfaces

**Files:**
- No source edits unless QA finds regressions

- [ ] Inspect `chapter-01` for left-rail legibility and active row readability.
- [ ] Inspect `chapter-04` for long-title wrapping under the new root contract.
- [ ] Inspect `glossary` and `bibliographical-references` for back-matter icon row balance.
- [ ] Inspect `public/book/index.html` or `cover.html` for intro title scale and rail rhythm.
- [ ] Only if a real regression is observed, make a targeted CSS adjustment and rerun:
  - `npm run test:site`
  - `npm run build:site`

---

## Acceptance Criteria

1. `/book` no longer relies on mdBook-generated `62.5%` as its effective font contract.
2. `theme/custom.css` explicitly declares the repo-owned root font size.
3. `scripts/test-site-render.sh` no longer protects the old `62.5%` contract.
4. Left-rail navigation is optically readable at desktop scale.
5. `General Conclusion`, `Glossary`, and `Bibliographical References` remain canonical mdBook-projected rows, with their icon treatment preserved.
6. `npm run test:site` passes.
7. `npm run build:site` passes.

---

## Risks

1. **Global `/book` rem amplification risk**
   - Any rem-authored reader chrome missed in the audit may become too large or too small after the root override.

2. **False sense of completion from static grep**
   - Static CSS assertions can pass while rendered optical balance still feels wrong.

3. **Mixed-unit maintenance risk**
   - If some surfaces stay px while others move to rem without rationale, future contributors may reintroduce scale confusion.

---

## Mitigations

1. Audit by MECE surface buckets rather than ad hoc selectors.
2. Move tests to the explicit root contract first, then migrate typography in controlled slices.
3. Finish with browser QA on representative long-title and back-matter pages.

---

## Recommended Execution Order

1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7

This order minimizes confusion: contract first, high-impact navigation next, then the rest of `/book` chrome.

