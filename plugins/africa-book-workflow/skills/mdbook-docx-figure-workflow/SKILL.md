---
name: mdbook-docx-figure-workflow
description: Use when modifying the Africa Book workspace, especially mdBook chapters, DOCX or PDF-derived figures, theme layout, or release validation commands.
---

# mdBook DOCX Figure Workflow

## Overview
This plugin packages the repo-specific workflow for the Africa Book project. Treat `editions/<locale>/content/`, `theme`, `scripts`, and edition-local image roots such as `editions/en/content/images` or `editions/fr/content/images` as source. Treat `public/` as generated output.

## When to Use
- A figure is correct in the PDF but wrong in HTML
- A chapter caption and its image reference drift apart
- A change touches `editions/<locale>/content/chapters/*.md`, `theme/custom.*`, `editions/<locale>/content/images/*`, or `scripts/*`
- You need to decide between the DOCX renderers and the PDF figure pipeline
- You need the right verification sequence before considering the site ready

## Workflow
1. Choose the source layer and edit there, not in `public/`.
2. For figures, prefer `npm run render:pdf-figures -- --figures N` when the figure is `shape_group`, `chart`, or `composite`, or when the PDF layout is the canonical result.
3. Use `render:docx-chart-figures`, `render:docx-shape-figures`, or `render:docx-vector-figures` only when native DOCX extraction is already stable or specifically required.
4. After figure or reference changes, rebuild the edition-local manifest with `python3 scripts/build_docx_figure_manifest.py --edition <locale>`.
5. Keep `scripts/test-site-render.sh` aligned with the published asset path and format.

## Verification
- Figure changes: `python3 scripts/check_docx_figures.py ...` plus the relevant `tests/docx_figures/*`
- Chapter text changes: `python3 scripts/check_docx_parity.py ... --chapter ...`
- Theme changes: targeted tests plus `npm run test:site` when feasible
- Full site sanity: `npm run build:site`

## Project Notes
- `mdbook` should resolve from `PATH`; on this machine the Homebrew fallback is `/opt/homebrew/bin/mdbook`.
- PDF rendering depends on `swift` and macOS `PDFKit`.
- PNG is an acceptable published fallback when the PDF pipeline cannot emit WebP.
- Repo facts and command inventory also live in `AGENTS.md`.
