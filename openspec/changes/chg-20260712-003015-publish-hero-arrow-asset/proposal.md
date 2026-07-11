## Why

The English homepage hero buttons reference `hero-arrow.svg`, but the static-site build does not publish that asset. Visitors receive a 404 and lose the intended visible arrow, even though the source asset and CSS reference both exist.

## What Changes

- Publish `assets/icons/homepage/hero-arrow.svg` with the English homepage assets.
- Replace the obsolete site-render assertion that forbids the generated asset with an assertion that requires it.
- Verify that the built English homepage loads the arrow without a 404 while preserving the existing button markup and navigation.

## Capabilities

### New Capabilities

- `homepage-hero-arrow-asset-delivery`: Deliver the asset referenced by English hero-button styling and validate its generated-site availability.

### Modified Capabilities

None.

## Impact

- Affected source: `scripts/build_site.mjs` and `scripts/test-site-render.sh`.
- Affected generated output: `public/assets/icons/homepage/hero-arrow.svg`.
- No URL, button-copy, navigation, CSS-selector, dependency, chapter, or French-homepage changes.
