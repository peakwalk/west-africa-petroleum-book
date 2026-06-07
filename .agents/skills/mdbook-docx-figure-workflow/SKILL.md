---
name: mdbook-docx-figure-workflow
description: Use when modifying the Africa Book mdBook project, especially chapter markdown, DOCX or PDF-derived figures, theme layout, or release validation commands.
---

# mdBook DOCX Figure Workflow

## Overview
This repo publishes an mdBook plus generated landing pages. Source edits belong in `src/chapters`, `theme`, `scripts`, and `src/images`. `public/` is generated output.

## When to Use
- A figure looks correct in the PDF but wrong in HTML
- A chapter has a caption without the right image reference
- A change touches `src/chapters/*.md`, `theme/custom.*`, `src/images/*`, or `scripts/*`
- You need to choose between the DOCX renderers and the PDF figure pipeline
- You need to run the right build or validation commands for a release-facing change

## Workflow
1. Choose the source layer.
   - Content: `src/chapters/*.md`, `src/SUMMARY.md`
   - Styles/behavior: `theme/custom.css`, `theme/custom.js`
   - Figure generation: `scripts/docx_figures/*`, `src/images/*`
   - Never hand-edit `public/*`
2. Pick the figure pipeline.
   - If a figure is `shape_group`, `chart`, or `composite`, or the DOCX-derived asset drifts from the PDF, use `npm run render:pdf-figures -- --figures N`.
   - Use `render:docx-chart-figures`, `render:docx-shape-figures`, or `render:docx-vector-figures` only when native DOCX extraction is stable or specifically required.
   - Current known PDF-backed figures: `17`, `23-32`
3. Sync references and metadata.
   - Update chapter markdown to point at the published asset
   - Rebuild the manifest with `python3 scripts/build_docx_figure_manifest.py`
   - If an asset path or format changed, update `scripts/test-site-render.sh`
4. Verify the smallest sufficient surface.
   - Figure changes: `python3 scripts/check_docx_figures.py ...` plus relevant `tests/docx_figures/*`
   - Chapter text changes: `python3 scripts/check_docx_parity.py ... --chapter ...`
   - Theme/layout changes: targeted tests plus `npm run test:site` when feasible
   - Full site sanity: `npm run build:site` or `npm run test:site`

## Tool Notes
- `mdbook` should resolve from `PATH`; on this machine the Homebrew fallback is `/opt/homebrew/bin/mdbook`.
- PDF figure rendering depends on `swift` and macOS `PDFKit`.
- WebP generation from the PDF pipeline is optional; `png` is a valid published asset when no encoder is available.

## Common Mistakes
- Editing `public/` directly
- Re-rendering figures without rebuilding `figure-manifest.json`
- Keeping a DOCX `svg` for a figure whose PDF layout is the canonical version
- Running only `mdbook build` after touching landing page scripts or figure assertions
