## Why

The landing build currently copies the entire `assets/` tree into both `public/assets/` and `public/fr/assets/`, including multiple historical image files that are no longer referenced by the landing generators, landing styles, or published landing markup. Those unused files increase repository noise and inflate the built asset payload even though no current landing route uses them.

This cleanup should stay conservative. It should remove only retired landing image variants that have no current runtime contract and keep the editable source assets that still feed active delivery surfaces, including `assets/images/upstream-atlas-hero-book.png` and `assets/images/upstream-atlas-favicon.png`.

## What Changes

- Remove a conservative set of unreferenced historical landing image assets from `assets/images/`.
- Refresh landing verification so both source and built asset trees fail if those retired files reappear.
- Leave active landing image contracts unchanged, including the current WebP nav logo, homepage SVG map panel, homepage WebP book cover, and favicon source chain.

## Capabilities

### New Capabilities
- `landing-unused-image-asset-cleanup`: The landing source tree and generated public asset trees exclude a defined set of retired historical landing image files.

### Modified Capabilities
- None.

## Impact

- Affected source assets removed from `assets/images/`:
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
- Affected verification: `tests/test_public_editions.py`, `scripts/test-site-render.sh`
- Affected generated output after rebuild: `public/assets/images/*`, `public/fr/assets/images/*`
