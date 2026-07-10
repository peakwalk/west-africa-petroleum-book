## Why

The current landing homepage regresses at narrow mobile widths in two different ways. At `390px`, the header keeps the desktop navigation visible and several homepage sections keep desktop grid behavior, which produces horizontal instability. At `320x568`, the primary hero CTA falls well below the first screen, the compact brand hit area is too small, and the stakeholder / summary modules still feel desktop-sized.

This follow-up needs to land now because the repository recently aligned several homepage sections to approved desktop references, and those refinements should not ship with a broken phone experience at either standard or compact mobile widths.

## What Changes

- Add a focused mobile-layout stabilization change for the landing homepage at phone and compact-phone widths.
- Update the shared landing mobile CSS so the header hides the desktop navigation, shows the existing compact mobile controls, keeps the brand mark inside a `44px`-class touch target, and aligns the action group to the approved narrow-header reference.
- Add the missing dedicated contact shortcut to the narrow header action group so phone layouts expose language switching, contact, and menu controls without text overlap.
- Reflow the homepage hero at phone widths so the supporting copy, CTA, and metrics stay on one reading track, with the CTA block still appearing before the metric grid, and tighten compact-phone spacing/gutters so the primary CTA remains near the first screen at `320x568`.
- Keep the `decision-strip` in a single-column mobile layout, but render the stakeholder cards in a denser two-column phone grid instead of a single vertical stack.
- Override the English `section-summary-modules` grid at mobile widths with selector specificity that beats the desktop section rule, remove fixed card-height assumptions, and compact the edition-cover treatment for small phones without collapsing it into a tall single-column card.
- Smooth the compact-phone breakpoint so `320px`, `360px`, and `390px` share the same hero reading order and aligned menu/content gutters instead of switching to a separate `<=360px` template.
- Split homepage-specific phone overrides into a dedicated responsive partial so mobile behavior stays maintainable without exceeding the repository stylesheet size guidance.
- Refresh landing-page verification to assert the intended phone-width header, hero, audience, summary, and compact-phone rules.
- Preserve approved desktop/tablet layout, copy, routes, and existing French compatibility structure outside the narrow-width overrides.

## Capabilities

### New Capabilities
- `homepage-mobile-layout-stability`: The landing homepage remains stable, readable, and action-prioritized at phone widths by switching to mobile navigation controls, keeping one hero reading order across compact and standard phones, placing the CTA before dense metrics, and converting desktop-heavy grids into phone-appropriate layouts.

### Modified Capabilities
- None.

## Impact

- Affected landing source generation: `scripts/shared/landing-shell.mjs`
- Affected landing styles: `assets/css/landing.header.css`, `assets/css/landing.responsive-mobile.css`, `assets/css/landing.responsive-mobile-homepage.css`, `assets/css/landing.css`
- Affected verification: `scripts/test-site-render.sh`
- Affected generated outputs after rebuild: `public/index.html`, `public/fr/index.html`, and related landing variants that consume the shared responsive stylesheet
