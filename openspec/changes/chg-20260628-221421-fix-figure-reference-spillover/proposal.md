## Why

Chapter 5 currently diverges from the published PDF because the DOCX extraction pipeline misclassifies a figure lead-in sentence as a figure caption spillover. That drops the introductory sentence before Figure 5 and leaves the chapter Markdown and rendered site with a truncated caption fragment instead of the intended prose-plus-caption structure.

## What Changes

- Tighten DOCX caption spillover detection so prose sentences that merely reference a figure number are preserved as paragraph body text.
- Add a regression test covering a chapter-opening figure lead-in sentence followed by a standalone figure caption.
- Regenerate the Chapter 5 Markdown semantic output indirectly through the corrected extraction behavior so future parity and rebuild workflows keep the proper text structure.

## Capabilities

### New Capabilities
- `docx-figure-reference-preservation`: DOCX semantic extraction preserves paragraph sentences that reference a figure before the actual figure caption, instead of truncating them into caption text.

### Modified Capabilities
- None.

## Impact

- Affected source files: `scripts/docx_parity/extract_docx.py`, `tests/docx_parity/test_extract_docx.py`
- Affected generated content semantics: Chapter 5 figure lead-in extraction and downstream Markdown parity output
- Validation surfaces: targeted DOCX extraction tests and Chapter 5 DOCX parity checks
- No new runtime dependencies
