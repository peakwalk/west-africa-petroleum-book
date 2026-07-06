## Why

The current homepage search surface does not match the approved reference. It repeats the heading as both an eyebrow and a title, and it uses a detached submit button instead of the wide integrated search field shown in the design.

The adjacent homepage `Browse by Topic` section also still reflects the earlier information-architecture draft rather than the approved six-card reference. It currently renders a large editorial heading and a ten-card grid instead of the compact icon-led topic strip shown in the design.

The bottom `section-summary-modules` area also still uses the older equal-width card layout and lacks the approved action links and checkmark list treatment shown in the supplied reference.

The user has provided concrete visual targets for all three surfaces. We need a narrow change that aligns the homepage search title and search field styling, the English `Browse by Topic` card layout, and the English summary-modules card row to those references while preserving the existing routes, localized copy, and French compatibility homepage behavior.

## What Changes

- Update homepage search-section markup to render a single visible centered title and an integrated pill-shaped search field with a leading search control/icon.
- Retune search-section spacing, width, border, radius, placeholder styling, responsive behavior, and search-scope chip iconography so the desktop and narrow-width layouts align with the approved reference.
- Replace the English homepage `Browse by Topic` editorial heading plus ten-card grid with a six-card topic reference strip that uses one visible section heading, local inline SVG icons, and the approved card copy hierarchy.
- Retune the English homepage summary-modules row so it matches the approved four-card reference, including non-uppercase card headings, green checkmark list markers, a wider current-edition card, and visible card action links.
- Preserve existing search routing and search-scope chips while refreshing the minimal homepage verification assertions for the new markup and CSS.
- Preserve the existing chapter destinations for the topic cards and keep the French compatibility homepage topic section on its current compact fallback layout.

## Capabilities

### New Capabilities
- `homepage-search-reference-alignment`: The generated homepage search section renders as the approved centered title plus integrated search-field composition without changing the underlying search destination contract.
- `homepage-topic-reference-alignment`: The generated English homepage browse-by-topic section renders as the approved six-card topical navigation surface without changing the underlying chapter destinations.
- `homepage-summary-reference-alignment`: The generated English homepage summary-modules row renders as the approved four-card closing reference surface without changing the underlying destination contracts.

### Modified Capabilities
- None.

## Impact

- Affected source generation: `scripts/shared/homepage-content.mjs`
- Affected source helpers: `scripts/shared/homepage-topic-reference.mjs`
- Affected landing styles: `assets/css/landing.discovery.css`, `assets/css/landing.homepage-v2.css`, `assets/css/landing.modules.css`, `assets/css/landing.responsive-tablet.css`, `assets/css/landing.responsive-mobile.css`
- Affected generated outputs after rebuild: `index.html`, `fr/index.html`, and `public/*` homepage variants
- Affected verification: `scripts/test-site-render.sh`
