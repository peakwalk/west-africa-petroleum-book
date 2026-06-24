## Why

The current `/book/` reader generates stable anchor targets for figures, tables, and numbered formulas, but body copy references such as `Figure 79`, `Table 17`, `Section 8.5`, and `Chapter 12` remain plain text. That leaves high-value navigation dead inside the reader and creates a maintenance burden when links are patched manually in chapter Markdown.

## What Changes

- Add a runtime body-copy cross-reference linker in `theme/custom.js`.
- Reuse the existing reader anchor contracts for `Figure N` -> `#figure-n` and `Table N` -> `#table-n`.
- Resolve `Section X.Y` references against the current chapter heading IDs already emitted by mdBook.
- Resolve `Chapter N` references against the published chapter routes already projected into the reader sidebar.
- Resolve `Equation X.Y` and `Formula X.Y` references against existing numbered formula anchors, using the current page first and published chapter routes when the equation chapter prefix points elsewhere.
- Skip unresolved references and keep them as plain text instead of generating broken links.

## Capabilities

### New Capabilities
- `book-reader-cross-references`: The `/book/` reader automatically links high-value textual references in body copy to the correct in-book anchor or chapter page without manual Markdown patching, including numbered equations when stable formula labels exist.

### Modified Capabilities
- None.

## Impact

- Affected source files: `theme/custom.js`, `scripts/test-site-render.sh`, `tests/test_theme_custom_css.py`
- Generated output affected through runtime enhancement: `/book/chapters/*.html`
- No new runtime dependencies
- No direct edits to published chapter Markdown are required for the reference-linking behavior itself
