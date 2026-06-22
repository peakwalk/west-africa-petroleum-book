## 1. Freeze boundaries and inventory the replacement manuscript

- [x] 1.1 Capture the replacement English TOC, front matter, back matter, figure/table counts, and old-to-new topic mapping in change-local evidence so the migration scope is explicit.
- [x] 1.2 Record the English-only cutover boundary: files that may change under `editions/en/**`, `resources/editions/en/reference.*`, and shared parser/build scripts, plus files that MUST stay unchanged under `editions/fr/**` and `resources/editions/fr/**`.
- [x] 1.3 Decide the target English chapter/file slug set from the replacement manuscript and document any intentional break with legacy deep links before content edits start.

## 2. Make the parity and extraction pipeline understand the new English structure

- [x] 2.1 Update `scripts/docx_parity/extract_docx.py` and related helpers so they recognize the replacement English front matter, chapter markers, and back-matter anchors instead of the retired six-chapter model.
- [x] 2.2 Add or update targeted parity tests/fixtures so `python3 scripts/check_docx_parity.py --edition en --docx <replacement-docx>` extracts real outline/body content instead of zero-block chapters.
- [x] 2.3 Preserve French extraction behavior by running the narrowest French parity regression checks after the English parser changes.

## 3. Rebuild English navigation and chapter markdown from the replacement manuscript

- [x] 3.1 Rewrite `editions/en/content/SUMMARY.md` to match the replacement English information architecture, including front matter, renamed/reordered chapters, and back matter.
- [x] 3.2 Replace the current English chapter markdown files under `editions/en/content/chapters/` with the replacement-manuscript-derived chapter set, including disclaimer/preface handling where the manuscript exposes them.
- [x] 3.3 Update any English landing or reader metadata that depends on English chapter structure or book title so the left sidebar and supporting pages stay consistent with the replacement manuscript.

## 4. Converge English figures, manifests, and chapter references

- [x] 4.1 Rebuild the English figure inventory and `editions/en/content/images/figure-manifest.json` against the replacement English DOCX/PDF.
- [x] 4.2 Re-render all changed English figures by the appropriate pipeline (`render:pdf-figures`, `render:docx-chart-figures`, `render:docx-shape-figures`, `render:docx-vector-figures`) and remove retired English-only assets from the published English tree.
- [x] 4.3 Update English chapter figure references, captions, and figure-related render assertions so the published English content and asset inventory match the replacement manuscripts.
- [x] 4.4 For replacement-English raster figures, keep same-numbered `png` exports, generate matching `webp` assets for web delivery, and allow single-image DOCX fallback when PDF cropping fails for a requested figure.

## 5. Cut over English aliases and verify the release

- [x] 5.1 Repoint `resources/editions/en/reference.docx` and `resources/editions/en/reference.pdf` to the replacement English source files only after English content and figures validate with explicit manuscript paths.
- [x] 5.2 Run the narrowest relevant release checks for the cutover: `python3 scripts/check_docx_parity.py --edition en`, `python3 scripts/check_docx_figures.py --edition en`, `npm run build:site`, targeted site tests, and French regression checks.
- [x] 5.3 Document the rollback procedure in the change notes and confirm that reverting the English aliases plus `editions/en/content/**` is sufficient to restore the prior English release without French changes.
