## Why

The current landing homepage regresses at narrow mobile widths in two different ways. At `390px`, the header keeps the desktop navigation visible and several homepage sections keep desktop grid behavior, which produces horizontal instability. At `320x568`, the primary hero CTA falls well below the first screen, the compact brand hit area is too small, and the stakeholder / summary modules still feel desktop-sized. A follow-up audit at `768x1024` also shows a mixed tablet/mobile state: the compact controls remain active, but the hero CTA drops back behind the metric grid and shrinks to an inline button. After the first breakpoint bridge was added, the same `768x1024` review still felt visually wrong because the page read like an oversized phone layout, with full-width CTA bars and an audience grid that left a large empty center gap. A later breakpoint audit around `1023px` and `1024px` exposed one more mixed state: tablet header controls were still active at `1023px`, but the hero/action density had already drifted back toward desktop, while `1024px` still kept the summary section in a tablet-like two-column layout even after the rest of the page switched to desktop density. The latest narrow-screen audit found three smaller polish gaps that still weaken the cutovers: the `320px` hero title still presses against the right edge, the `767px` upper phone width stays too sparse in one-column content grids, and the `861px` through `1119px` hero action track becomes visually left-heavy near the tablet upper bound.

This follow-up needs to land now because the repository recently aligned several homepage sections to approved desktop references, and those refinements should not ship with a broken phone experience at either standard or compact mobile widths.

## What Changes

- Add a focused mobile-layout stabilization change for the landing homepage at phone and compact-phone widths.
- Update the shared landing mobile CSS so the header hides the desktop navigation, shows the existing compact mobile controls, keeps the brand mark inside a `44px`-class touch target, and aligns the action group to the approved narrow-header reference.
- Add the missing dedicated contact shortcut to the narrow header action group so phone layouts expose language switching, contact, and menu controls without text overlap.
- Reflow the homepage hero at phone widths so the supporting copy, CTA, and metrics stay on one reading track, with the CTA block still appearing before the metric grid, and tighten compact-phone spacing/gutters so the primary CTA remains near the first screen at `320x568`.
- Add a tablet-portrait bridge from `768px` through `860px` so the tablet header treatment can remain intact while the hero keeps the same CTA-before-metrics reading priority as the approved narrow-width layout, but with a restrained content track, a denser `3 x 2` metric grid, and a denser `3 x 2` audience grid that feels tablet-scaled rather than phone-scaled.
- Add a wide-tablet bridge from `861px` through `1119px` so the compact tablet header controls remain paired with tablet-density hero, audience, topics, countries, and summary grids instead of falling into a tablet/desktop hybrid state near `1024px`.
- Delay the small-desktop landing header onset from `1024px` to `1120px` so desktop navigation, logo spacing, and dense section grids begin together.
- Keep the homepage summary modules from staying in a desktop four-column layout through `1119px` width by switching them to a two-column tablet layout with content-driven card heights.
- Add a large-phone bridge from `700px` through `767px` so the homepage content grids can condense into two columns before the tablet header mode begins, reducing the abrupt density jump at the top end of phone widths.
- Add a `<=320px` hero-title micro-adjustment so the compact-phone headline regains a visible right gutter without changing the rest of the CTA/copy track.
- Make the `861px` through `1119px` hero content track slightly fluid instead of fixed-width so the wide-tablet hero keeps its tablet reading order without becoming visually left-weighted near `1119px`.
- Keep the `decision-strip` in a single-column mobile layout, but render the stakeholder cards in a denser two-column phone grid instead of a single vertical stack.
- Override the English `section-summary-modules` grid at mobile widths with selector specificity that beats the desktop section rule, remove fixed card-height assumptions, and compact the edition-cover treatment for small phones without collapsing it into a tall single-column card.
- Smooth the compact-phone breakpoint so `320px`, `360px`, and `390px` share the same hero reading order and aligned menu/content gutters instead of switching to a separate `<=360px` template.
- Split homepage-specific phone overrides into a dedicated responsive partial so mobile behavior stays maintainable without exceeding the repository stylesheet size guidance.
- Refresh landing-page verification to assert the intended phone-width header, hero, audience, summary, and compact-phone rules.
- Preserve approved desktop/tablet layout, copy, routes, and existing French compatibility structure outside the narrow-width overrides.

## Capabilities

### New Capabilities
- `homepage-mobile-layout-stability`: The landing homepage remains stable, readable, and action-prioritized across compact phones, standard phones, narrow portrait tablets, and wide tablets by switching to mobile navigation controls, keeping one hero reading order across nearby narrow widths, placing the CTA before dense metrics, and converting desktop-heavy grids into tablet- or phone-appropriate layouts until the true desktop breakpoint begins.

### Modified Capabilities
- None.

## Impact

- Affected landing source generation: `scripts/shared/landing-shell.mjs`
- Affected landing styles: `assets/css/landing.header.css`, `assets/css/landing.responsive-mobile.css`, `assets/css/landing.responsive-mobile-homepage.css`, `assets/css/landing.responsive-tablet.css`, `assets/css/landing.css`
- Affected verification: `scripts/test-site-render.sh`
- Affected generated outputs after rebuild: `public/index.html`, `public/fr/index.html`, and related landing variants that consume the shared responsive stylesheet
