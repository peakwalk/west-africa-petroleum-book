## Context

The homepage already uses optimized formats for its heaviest visual surfaces: the hero background is delivered as WebP and the West Africa map panel is delivered as SVG because that vector file is both smaller and sharper than the raster alternatives. The remaining homepage outlier is the current-edition cover card, which still points at `assets/images/upstream-atlas-hero-book.png`.

That PNG asset is about `1.8MB` at `1024x1536`, while the card styles render it at roughly a `100px`-wide track. The change should stay narrow: optimize only this homepage cover surface, keep the map SVG contract untouched, and avoid broader landing-page image rewrites.

## Goals / Non-Goals

**Goals:**
- Reduce delivered bytes for the English homepage current-edition cover image.
- Mark the English homepage current-edition cover as non-critical so it does not compete with the hero for initial loading.
- Keep the change limited to shared homepage generation, one repo-owned asset, and landing-page verification.

**Non-Goals:**
- Redesign the summary module layout or change the cover artwork itself.
- Convert the homepage map panel from SVG to WebP.
- Rework other landing-page PNG assets whose measured savings are negligible or negative.

## Decisions

### Decision: Ship a homepage-specific optimized WebP cover asset
The homepage will add `assets/images/upstream-atlas-hero-book.webp`, generated from the existing PNG at a homepage-appropriate size. A `640x960` WebP keeps enough detail for the current card surface while dropping the asset well below the original PNG size.

Alternative considered:
- Keep the original PNG and only add lazy loading. Rejected because it preserves the main byte-cost problem.

### Decision: Reference the optimized asset directly from the shared homepage generator
`scripts/shared/homepage-content.mjs` will point the current-edition card image `src` at the new WebP asset and add `loading="lazy"` plus `decoding="async"`. The landing homepage already depends on WebP elsewhere, so a direct `src` swap is narrower than introducing `picture` markup and additional layout selectors just for this card.

Alternative considered:
- Use a `picture` element with PNG fallback. Rejected because it adds markup and CSS churn without improving the actual homepage contract in browsers that already need WebP support for the existing hero surface.

### Decision: Guard both markup and built-asset size in regression tests
The unit-level homepage generation test will assert the WebP path and loading hints, and `scripts/test-site-render.sh` will assert the built site no longer emits the PNG path for the homepage cover and that the built WebP asset stays below an explicit size cap.

Alternative considered:
- Rely only on manual size inspection. Rejected because the regression is easy to reintroduce through later rebuilds or asset swaps.

## Risks / Trade-offs

- [WebP-only cover depends on existing landing WebP support] -> Accept this because the landing hero already relies on WebP assets today.
- [Homepage-specific resized asset is not suitable for full-screen reuse] -> Keep the original PNG as the editable source of truth and scope the new WebP to the homepage card only.
- [Future cover-art updates could regenerate a larger file] -> Add a built-asset size assertion so oversized replacements fail quickly.

## Migration Plan

1. Add failing homepage regression checks for the optimized cover path and loading hints.
2. Generate the homepage WebP cover asset from the existing PNG source.
3. Update the shared homepage generator to reference the WebP cover with lazy and async decoding hints.
4. Rebuild the site and run homepage-focused verification plus OpenSpec validation.
5. If rollback is needed, switch the homepage cover back to the PNG source, remove the WebP asset reference, and rebuild the site.

## Open Questions

- None for this change.
