# Outline Reference Section Gating Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hide right-rail `Figures`, `Tables`, and `Formulas` sections on pages whose source content does not provide that content type.

**Architecture:** Extend `reader-page-meta.json` with page-level reference-section flags derived from chapter source markdown, then gate the existing right-rail section renderer in `theme/custom.js` with both metadata and collected DOM items. Keep the existing DOM annotation pipeline and only tighten visibility decisions.

**Tech Stack:** Node.js ESM build scripts, browser-side vanilla JavaScript in `theme/custom.js`, Python `unittest`.

---

### Task 1: Lock the behavior with regression tests

**Files:**
- Create: `tests/test_reader_page_meta.py`
- Modify: `tests/test_theme_custom_css.py`

- [ ] Add a regression test that runs `node scripts/build_reader_page_meta.mjs` and asserts chapter 1-6 metadata flags for `figures`, `tables`, and `formulas`.
- [ ] Add a source-level JS regression test that asserts `theme/custom.js` reads the new page metadata and uses it to gate right-rail section rendering.

### Task 2: Generate page-level reference-section metadata

**Files:**
- Modify: `scripts/build_reader_page_meta.mjs`

- [ ] Add markdown analyzers that detect figures, tables, and formulas for each page.
- [ ] Persist the result under a new `referenceSections` object in `reader-page-meta.json` without disturbing existing fields.

### Task 3: Gate right-rail sections by metadata and collected items

**Files:**
- Modify: `theme/custom.js`

- [ ] Load the current page's `referenceSections` metadata in the outline-section installer.
- [ ] Keep existing DOM collection, but only show each section when metadata allows it and items exist.
- [ ] Re-run outline visibility sync after async metadata-backed section rendering completes.

### Task 4: Verify the focused surface

**Files:**
- Test: `tests/test_reader_page_meta.py`
- Test: `tests/test_theme_custom_css.py`

- [ ] Run `python3 -m unittest tests.test_reader_page_meta tests.test_theme_custom_css -v`
- [ ] Review output and confirm the new gating behavior is covered without unrelated failures.
