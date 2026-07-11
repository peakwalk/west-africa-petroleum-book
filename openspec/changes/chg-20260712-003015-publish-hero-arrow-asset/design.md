## Context

The English homepage renders `.hero-panel-v2` buttons whose `::after` pseudo-element loads `assets/icons/homepage/hero-arrow.svg`. The source SVG exists, but the static build's allowlist omits it. The generated `public/` directory therefore returns a 404 for the CSS background URL.

`hero-panel-v2` is an English homepage surface. The French compatibility homepage does not use it, so publishing the asset to the English-only output keeps the existing edition asset boundary intact.

## Goals / Non-Goals

**Goals:**

- Publish the existing arrow SVG at the URL referenced by the generated English CSS.
- Restore the intended hero-button arrow without changing the CSS selector, markup, or link behaviour.
- Make the output asset's presence a site-render contract.

**Non-Goals:**

- Redesigning hero buttons or replacing the SVG with text or a different icon.
- Publishing unused legacy homepage icons.
- Changing French output, responsive rules, navigation, or source SVG artwork.

## Decisions

### Publish the existing source asset as an English-only asset

Add `icons/homepage/hero-arrow.svg` to `ENGLISH_ONLY_PUBLIC_ASSET_PATHS`.

The generated English CSS resolves its relative URL to `public/assets/icons/homepage/hero-arrow.svg`, which this manifest entry produces exactly. Adding the asset to the shared list was rejected because the French homepage does not use the selector. Replacing the background with a text arrow or an existing sprite symbol was rejected because either changes the approved arrow artwork or requires unnecessary markup and style changes.

### Make the build test assert the positive contract

The site-render script will assert that the English generated asset exists and will retain the French absence assertion.

This reverses the stale negative assertion responsible for allowing the broken production output while preserving the project's selective-public-asset policy.

## Risks / Trade-offs

- **An asset cleanup later removes the manifest entry.** → The positive generated-asset assertion fails during site validation.
- **The asset leaks into French output.** → The existing French absence assertion remains in place.
- **The SVG content changes unexpectedly.** → This change reuses the existing source file; no artwork is copied or edited.

## Migration Plan

1. Build the site to regenerate `public/assets/icons/homepage/hero-arrow.svg`.
2. Deploy through the normal static-site release process.
3. Roll back by removing the English-only manifest entry and restoring the former test expectation; no URL or data migration is involved.

## Open Questions

None.
