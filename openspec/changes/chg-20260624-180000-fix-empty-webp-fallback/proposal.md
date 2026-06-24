## Why

Figure 11 is currently broken in the English web book because the published asset pipeline prefers `figure-011.webp` even when that file is zero bytes and a valid `figure-011.png` exists beside it. The same selection bug can silently publish future broken figures unless the inventory and validation layers both reject empty preferred assets.

## What Changes

- Teach the figure inventory publisher to ignore zero-byte candidate assets and fall back to the next valid format for the same figure stem.
- Extend DOCX figure coverage validation to fail when Markdown or manifest-selected figure assets are empty files.
- Repair the English Figure 11 published asset so the current `/book/` build no longer ships a broken image.
- Rebuild the English figure manifest so future rebuilds keep the corrected asset selection.

## Capabilities

### New Capabilities
- `figure-asset-fallback`: Figure asset publication and validation prefer non-empty published assets, automatically falling back from an empty preferred WebP to a valid PNG and failing validation when an empty asset would otherwise be shipped.

### Modified Capabilities
- None.

## Impact

- Affected source files: `scripts/docx_figures/inventory.py`, `scripts/check_docx_figures.py`, `tests/docx_figures/test_inventory.py`, `tests/test_book_editions.py`
- Affected published assets and metadata: `editions/en/content/images/figure-011.webp`, `editions/en/content/images/figure-manifest.json`
- Generated output affected after rebuild: `public/book/images/figure-011.webp`, `public/book/images/figure-manifest.json`
- No new runtime dependencies
