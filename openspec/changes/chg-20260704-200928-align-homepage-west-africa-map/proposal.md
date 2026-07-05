## Why

The current homepage map overview diverges sharply from the approved reference. It uses an abstract landmass, oversized editorial typography, and an orange CTA treatment, so the section no longer reads like a political West Africa entry surface.

The user has provided a concrete target image for this module. We need a narrow repo-owned change that aligns the homepage map panel to that approved west-coast composition while preserving the existing country-analysis routing contract.

Follow-up visual review also showed that the homepage still mixes several breakpoint conventions (`700 / 900 / 1100 / 1200 / 1201`) with fluid desktop typography. That makes desktop compositions drift between 1440px and wider screens, especially in the map overview copy. The homepage needs an explicit responsive range model so phone, pad, small desktop, and locked desktop behave predictably.

The same review also exposed a compatibility problem in the primary country-card entry path: homepage flags still depend on external SVG sprite `<use>` references, which can disappear in some standalone/static renderers. The homepage should inline the shared flag sprite once so the cards remain reliable wherever the built page is embedded or previewed.

## What Changes

- Replace the current abstract map panel with a west-coast political reference panel that visually matches the approved composition, including the Cape Verde inset and coastline-oriented mainland.
- Retune the map-overview copy, spacing, typography, and CTA treatment so the left column aligns with the approved compact presentation.
- Preserve the existing country deep links by keeping map hotspots wired to the same destinations as the country cards, even though the visible panel artwork changes.
- Rationalize homepage breakpoint handling around four explicit ranges: `0-767` phone, `768-1023` pad, `1024-1439` small desktop, and `1440+` desktop locked.
- Inline the shared country-flag sprite in homepage output and switch country-card flags to local fragment references instead of external sprite URLs.
- Add or refresh the minimal build/test assertions needed for the updated asset, markup, and homepage output.

## Capabilities

### New Capabilities
- `homepage-map-reference-alignment`: The homepage map overview renders as the approved west-coast political reference module while preserving accessible country-routing hotspots into the existing book.

### Modified Capabilities
- None.

## Impact

- Affected source generation: `scripts/shared/homepage-content.mjs`
- Affected landing styles: `assets/css/landing.discovery.css`, `assets/css/landing.homepage-v2.css`, `assets/css/landing.header.css`, `assets/css/landing.responsive-tablet.css`, `assets/css/landing.responsive-mobile.css`
- Affected visual assets: `assets/images/*`, `assets/icons/*`
- Affected generated outputs after rebuild: `index.html`, `public/index.html`, and localized homepage variants
- Affected verification: `scripts/test-site-render.sh`, `tests/test_homepage_country_flags.py`, plus a local visual screenshot check
