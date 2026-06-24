## 1. OpenSpec and failing tests

- [x] 1.1 Add the empty-WebP fallback proposal, design, and capability spec.
- [x] 1.2 Add failing tests for zero-byte WebP fallback and for the built English Figure 11 asset being non-empty.

## 2. Asset publication and validation

- [x] 2.1 Update `scripts/docx_figures/inventory.py` so published asset selection skips zero-byte files and falls back to the next valid format for the same figure stem.
- [x] 2.2 Update `scripts/check_docx_figures.py` to fail on zero-byte Markdown targets and zero-byte manifest-selected assets.

## 3. Repair and verify

- [x] 3.1 Regenerate the English `figure-011.webp` asset and rebuild `editions/en/content/images/figure-manifest.json`.
- [x] 3.2 Run the targeted inventory and build tests plus the narrow figure coverage checks needed to confirm the fix.
- [x] 3.3 Rebuild the site and confirm the published English Figure 11 asset is no longer empty.
