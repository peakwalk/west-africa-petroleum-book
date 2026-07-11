## 1. Source intake and mapping protection

- [x] 1.1 Download the three UA-19 attachments to a temporary staging directory, record their hashes and dimensions, and verify that their subjects match Figures 9, 41, and 69 before editing.
- [x] 1.2 Confirm the source-to-target mapping: 008 to 009, 040 to 041, and 068 to 069; confirm that the existing Figure 8, 40, and 68 assets are out of scope.

## 2. Reviewed figure production

- [x] 2.1 Revise the staged Figure 9 source artwork with the two approved petroleum-product terminology changes while preserving product order and visual layout.
- [x] 2.2 Revise the staged Figure 41 source artwork so Integration and Modelling outputs feed Evaluation and Recovery Options, and remove the dangling Box 2 arrow.
- [x] 2.3 Revise the staged Figure 69 source artwork with the approved PSC revenue flow, recoverable-cost categories, terminology, and Profit Oil / Profit Gas description.
- [x] 2.4 Save the revised source artwork as English `figure-009.png`, `figure-041.png`, and `figure-069.png`; generate their matching lossless WebP publication assets without editing `public/`.

## 3. Metadata and regression coverage

- [x] 3.1 Add a focused regression test that asserts the UA-19 source-to-target asset mapping and protects the adjacent Figure 8, 40, and 68 assets from this change.
- [x] 3.2 Rebuild `editions/en/content/images/figure-manifest.json` and review any resulting diff for unintended reference or caption changes.
- [x] 3.3 Strengthen the mapping regression test to assert that the Figure 8, 40, and 68 PNG assets retain their expected hashes and cannot be replaced by the UA-19 source artwork.

## 4. Paired visual-review evidence

- [x] 4.1 Build the current English reader and capture baseline screenshots of Figures 9, 41, and 69 at the agreed fixed viewport under `output/playwright/ua-19-technical-figure-corrections/baseline/` before modifying target assets.
- [x] 4.2 After implementation and site rebuild, capture matching updated screenshots of Figures 9, 41, and 69 with the same route, browser engine, viewport, and full-page setting under `output/playwright/ua-19-technical-figure-corrections/updated/`.
- [x] 4.3 Deliver the paired baseline and updated screenshots together for human review, identifying the figure number for every pair.

## 5. Validation and acceptance

- [x] 5.1 Run the focused figure tests and `python3 scripts/check_docx_figures.py --edition en`.
- [x] 5.2 Build the site and run the site-render validation without hand-editing generated output.
- [x] 5.3 Visually inspect the rendered English Figures 9, 41, and 69 for wording, arrow endpoints, PSC flow, cropping, typography, captions, and figure references.
