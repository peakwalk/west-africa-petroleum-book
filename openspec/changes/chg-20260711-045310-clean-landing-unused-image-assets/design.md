## Context

The landing pages now reference a narrower image set than the asset tree still carries. Current contracts use:
- `assets/images/upstream-atlas-nav-logo.webp` for the landing header/footer lockup
- `assets/images/upstream-atlas-icon.png` for the compact mark
- `assets/images/upstream-atlas-hero-book.webp` for the English homepage current-edition card
- `assets/images/homepage-west-africa-map-panel.svg` for the homepage map panel
- `assets/images/upstream-atlas-favicon.png` as the editable favicon source plus the split landing derivatives

At the same time, `scripts/build_site.mjs` copies the full `assets/` tree into both locale outputs. That means clearly retired files still ship into `public/assets/images/` and `public/fr/assets/images/` even when the generated HTML never references them. A conservative scan identified a safe removal set worth about `2.9MB` in source assets alone.

## Goals / Non-Goals

**Goals:**
- Remove only retired landing image files with no current runtime references.
- Keep active source-of-truth image files that still feed current optimized delivery.
- Add regression checks so the retired files stay absent from both source and built asset trees.

**Non-Goals:**
- Rework book-reader theme assets or chapter-page image contracts.
- Delete active editable source files such as `upstream-atlas-hero-book.png` or `upstream-atlas-favicon.png`.
- Revisit the `assets/icons/homepage-cropped/*.png` source set in this pass.

## Decisions

### Decision: Limit cleanup to a conservative retired asset list
This change removes only image files under `assets/images/` that have no current references in landing generators, landing styles, or landing verification contracts.

Retired files:
- `cover.png`
- `homepage-west-africa-map-panel.png`
- `homepage-west-africa-map-panel.webp`
- `homepage-west-africa-map-panel@2x.png`
- `prototype-hero-cutout.png`
- `prototype-hero-edge-left.png`
- `prototype-hero-edge-right.png`
- `prototype-hero-grayscale-left.png`
- `prototype-hero-grayscale-right.png`
- `prototype-hero-overlay.png`
- `upstream-atlas-hero-v2-photo.png`
- `upstream-atlas-logo.png`
- `upstream-atlas-nav-logo.png`

Alternative considered:
- Delete every unreferenced landing PNG or old hero variant in one pass. Rejected because some files are still documented as editable source material or need a separate review to avoid unnecessary churn.

### Decision: Assert absence in both source and built outputs
`tests/test_public_editions.py` will guard the source tree so the retired files stay deleted, and `scripts/test-site-render.sh` will guard the built site so asset copying does not republish them into `public/assets/images/` or `public/fr/assets/images/`.

Alternative considered:
- Only delete the files and rely on future `git diff` review. Rejected because `scripts/build_site.mjs` copies assets wholesale, so regressions would be easy to miss.

## Risks / Trade-offs

- [A file could still be useful as informal design history] -> Accept this for the listed set because there is no current runtime reference and the user explicitly asked to clean historical landing assets.
- [The cleanup is intentionally incomplete] -> Accept this because the conservative scope avoids deleting active source chains or broader theme assets without a separate review.

## Migration Plan

1. Add failing regression checks for the retired asset list in source and built output validation.
2. Delete the retired source assets from `assets/images/`.
3. Rebuild the site so `public/assets/images/` and `public/fr/assets/images/` no longer contain those files.
4. Run targeted landing tests, site render validation, and OpenSpec validation.
5. If rollback is needed, restore the deleted asset files and remove the absence assertions.

## Open Questions

- None for this change.
