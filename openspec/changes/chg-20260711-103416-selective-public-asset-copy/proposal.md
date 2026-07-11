## Why

The current site build copies the full `assets/` tree into both `public/assets/` and `public/fr/assets/` even though the two output trees do not need the same runtime assets. That behavior republishes source-only images such as `upstream-atlas-hero-book.png`, carries English-homepage-only assets into the French site tree, and keeps locale-irrelevant icon groups in outputs that never reference them.

The next step should improve delivery without changing page markup or theme behavior. The safest approach is to replace whole-tree copying with a curated public-asset manifest that preserves the current runtime contracts and excludes source-only or locale-irrelevant files.

## What Changes

- Replace full-tree public asset copying with explicit asset manifests in `scripts/build_site.mjs`.
- Keep shared runtime assets available to both English and French outputs.
- Limit English-homepage-only assets to `public/assets/` and omit them from `public/fr/assets/`.
- Stop copying source-only image files into either public asset tree.
- Stop copying English-root icon directories that no generated page references at runtime.

## Capabilities

### New Capabilities
- `selective-public-asset-copy`: The site build publishes only the runtime asset subsets needed by each output tree instead of copying the whole source asset tree.

### Modified Capabilities
- `landing-site-build`: The public site build keeps existing page behavior while reducing copied asset surface area per locale.

## Impact

- Affected build logic: `scripts/build_site.mjs`
- Affected verification: `scripts/test-site-render.sh`
- Affected generated output after rebuild:
  - `public/assets/**`
  - `public/fr/assets/**`
- Key assets intentionally omitted from copied outputs:
  - `public/assets/images/upstream-atlas-hero-book.png`
  - `public/assets/images/prototype-hero-graywhite-left.png`
  - `public/assets/images/prototype-hero-graywhite-right.png`
  - `public/assets/icons/country-flags.svg`
  - `public/assets/icons/homepage/*`
  - `public/assets/icons/stakeholders/*`
  - `public/assets/icons/topics/*`
  - `public/fr/assets/images/upstream-atlas-hero-book.webp`
  - `public/fr/assets/images/homepage-west-africa-map-panel.svg`
  - `public/fr/assets/icons/homepage-cropped/*.webp`
  - `public/fr/assets/icons/homepage/hero-*.svg`
  - `public/fr/assets/icons/homepage/icon-close.svg`
  - `public/fr/assets/icons/homepage/icon-menu.svg`
  - `public/fr/assets/icons/homepage/icon-start-reading.svg`
  - `public/fr/assets/icons/homepage/icon-production.svg`
  - `public/fr/assets/icons/homepage/icon-exploration.svg`
  - `public/fr/assets/icons/homepage/icon-fiscal.svg`
  - `public/fr/assets/icons/homepage/icon-regulation.svg`
