## 1. OpenSpec and regression scope

- [x] 1.1 Write the proposal, design, spec, and Chinese companion files for the homepage mobile-layout stabilization change.

## 2. Mobile landing layout fix

- [x] 2.1 Add landing verification checks that fail when the phone-width header keeps desktop navigation visible or when the phone-width section grids stop stacking.
- [x] 2.2 Update the shared header/mobile responsive styles so the phone header exposes language, contact, and menu controls with a compact-brand touch target that matches the supplied reference.
- [x] 2.3 Add homepage-specific phone overrides that reorder the hero CTA ahead of the metric grid, keep stakeholder cards in a denser two-column mobile grid, and remove desktop-height assumptions from the summary modules.
- [x] 2.4 Split homepage-only phone overrides into a dedicated responsive partial so the repository stylesheet size limit stays satisfied.
- [x] 2.5 Smooth the compact-phone breakpoint so `320px`, `360px`, and `390px` keep one hero reading order, aligned menu gutters, and a denser current-edition card.

## 3. Rebuild and verification

- [x] 3.1 Rebuild the site and run the narrowest useful landing-page verification command for the new phone-width rules.
- [x] 3.2 Re-run headless mobile Playwright captures at `390px` width and `320x568` compact-phone size to confirm the homepage no longer overflows horizontally and keeps the primary CTA near the first screen.
- [x] 3.3 Re-run headless mobile Playwright captures at `320x568`, `360x640`, and `390x844` to confirm the compact-phone gutter alignment and the absence of a breakpoint-order jump.
