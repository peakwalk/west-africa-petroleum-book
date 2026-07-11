## Why

The landing asset tree still contains a group of historical image variants that are no longer referenced by generated landing HTML, generated landing CSS, or the current book shell. Because `scripts/build_site.mjs` copies the full `assets/` tree into both English and French public outputs, these dead variants keep shipping even though no runtime surface points at them.

This cleanup should remain conservative and should keep clear distance from the current book-theme asset chain. In particular, it should not touch the active `prototype-hero-graywhite-*.webp` files or their retained PNG source backups.

## What Changes

- Remove a second batch of unreferenced historical landing image variants from `assets/images/`.
- Update landing verification so both the source tree and built public trees fail if those variants reappear.
- Leave active landing and book-theme asset contracts unchanged.

## Capabilities

### New Capabilities
- `landing-unreferenced-asset-variant-cleanup`: The landing source tree and generated public asset trees exclude a defined set of unreferenced historical image variants that are no longer part of any runtime contract.

### Modified Capabilities
- None.

## Impact

- Affected source assets removed from `assets/images/`:
  - `homepage-cabo-verde-inset.svg`
  - `prototype-hero-dusk.webp`
  - `prototype-hero-night.webp`
  - `prototype-hero-sunset-right.webp`
  - `prototype-hero-sunset-source.webp`
  - `prototype-hero.jpg`
  - `upstream-atlas-hero-v2-photo-right-fade.webp`
  - `upstream-atlas-hero-v3-clean.webp`
  - `upstream-atlas-hero-v4-clean.webp`
  - `upstream-atlas-hero-v5-soft-left.webp`
  - `upstream-atlas-hero-v6-soft-left.webp`
  - `upstream-atlas-wordmark.png`
  - `west-africa-intelligence-overlay.svg`
- Affected verification: `tests/test_public_editions.py`, `scripts/test-site-render.sh`
- Affected generated output after rebuild: `public/assets/images/*`, `public/fr/assets/images/*`
