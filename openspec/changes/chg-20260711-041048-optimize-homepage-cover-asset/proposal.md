## Why

The landing homepage still ships the current-edition cover card from a `1024x1536` PNG asset that is about `1.8MB`, even though the card renders the image at a much smaller size and below the primary hero. That single non-critical image dominates homepage image bytes and delays a surface that does not need full-resolution PNG delivery.

## What Changes

- Add a repo-owned optimized WebP cover asset for the homepage current-edition card.
- Update the shared homepage generator so the current-edition cover uses the optimized WebP asset and non-critical loading hints.
- Keep the homepage map panel on its existing SVG contract and leave other landing-page image formats unchanged.
- Refresh homepage verification so regressions fail when the built landing pages fall back to the heavy PNG cover asset.

## Capabilities

### New Capabilities
- `homepage-cover-asset-delivery`: The English landing homepage renders the current-edition cover card from an optimized WebP asset with non-critical loading behavior.

### Modified Capabilities
- None.

## Impact

- Affected homepage source generation: `scripts/shared/homepage-content.mjs`
- Affected homepage source assets: `assets/images/upstream-atlas-hero-book.png`, `assets/images/upstream-atlas-hero-book.webp`
- Affected verification: `tests/test_public_editions.py`, `scripts/test-site-render.sh`
- Affected generated output after rebuild: `public/index.html`, `public/assets/images/upstream-atlas-hero-book.webp`, `public/fr/assets/images/upstream-atlas-hero-book.webp`
