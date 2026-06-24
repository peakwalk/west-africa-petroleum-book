## Context

The current English figure asset set contains a valid `figure-011.png` and a zero-byte `figure-011.webp`. Chapter Markdown still uses canonical `.webp` references, while the figure inventory builder publishes asset candidates by extension priority only. That combination makes both the manifest and the chapter page prefer a broken asset. Existing coverage validation only checks file existence, so a zero-byte published asset is treated as healthy.

## Goals / Non-Goals

**Goals:**
- Preserve canonical `.webp` naming when the WebP file is valid.
- Skip empty published asset files during figure inventory selection and fall back to the next valid format for the same stem.
- Make figure coverage validation fail when a referenced or manifest-selected figure asset is empty.
- Repair the current English Figure 11 asset without broad chapter rewrites.

**Non-Goals:**
- Reformat all chapter image references to `.png`.
- Redesign the entire figure rendering pipeline.
- Add content-aware image corruption detection beyond the zero-byte guard.

## Decisions

### Decision: Filter zero-byte files at inventory selection time
The inventory publisher already centralizes published asset preference in `_published_asset_candidates`. That is the narrowest place to reject empty WebP files and choose a valid PNG fallback without changing figure numbering or chapter semantics.

Alternative considered:
- Rewrite chapter Markdown references dynamically at build time. Rejected because it is broader, touches more content, and still needs an inventory rule for manifest correctness.

### Decision: Treat empty referenced assets as validation failures
`check_docx_figures.py` currently only enforces existence. Extending it to reject zero-byte files closes the gap for chapter Markdown that still points at canonical `.webp` assets. This gives the build chain a hard regression signal even when a fallback candidate exists elsewhere.

Alternative considered:
- Rely only on unit tests around `_published_asset_candidates`. Rejected because it would not guard hand-edited chapter references or stale empty assets already present on disk.

### Decision: Regenerate only Figure 11’s WebP asset
The current user-facing failure is isolated to Figure 11. Re-rendering that single bitmap WebP keeps the fix small, preserves the existing canonical reference name, and avoids unrelated chapter churn.

## Risks / Trade-offs

- [Stale empty assets outside published references] → Validation only catches assets that are either referenced by Markdown or selected by the manifest. Unused empty files may remain on disk, which is acceptable for this bugfix scope.
- [Canonical name expectations] → Some tests and source chapters assume `.webp` names. Regenerating `figure-011.webp` instead of rewriting references preserves that contract.
- [Future non-zero corrupt files] → The new guard only detects empty files. If future corruption produces non-zero invalid binaries, a stronger integrity check would still be needed.

## Migration Plan

1. Add failing tests for empty-WebP fallback and for the built English Figure 11 asset being non-empty.
2. Implement empty-file filtering in `scripts/docx_figures/inventory.py`.
3. Extend `scripts/check_docx_figures.py` to report empty Markdown targets and empty manifest-selected assets.
4. Regenerate `editions/en/content/images/figure-011.webp`.
5. Rebuild the English figure manifest and full site output.
6. If rollback is needed, restore the previous inventory/checker behavior and the prior Figure 11 asset, then rebuild the manifest.

## Open Questions

- None for this change.
