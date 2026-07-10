## 1. OpenSpec and regression scope

- [x] 1.1 Write the proposal, design, spec, and Chinese companion files for the homepage mobile-layout stabilization change.

## 2. Mobile landing layout fix

- [x] 2.1 Add landing verification checks that fail when the phone-width header keeps desktop navigation visible or when the phone-width section grids stop stacking.
- [x] 2.2 Update the shared header/mobile responsive styles so the phone header exposes language, contact, and menu controls with a compact-brand touch target that matches the supplied reference.
- [x] 2.3 Add homepage-specific phone overrides that reorder the hero CTA ahead of the metric grid, keep stakeholder cards in a denser two-column mobile grid, and remove desktop-height assumptions from the summary modules.
- [x] 2.4 Split homepage-only phone overrides into a dedicated responsive partial so the repository stylesheet size limit stays satisfied.
- [x] 2.5 Smooth the compact-phone breakpoint so `320px`, `360px`, and `390px` keep one hero reading order, aligned menu gutters, and a denser current-edition card.
- [x] 2.6 Add a `768px`-`860px` tablet-portrait bridge so the hero keeps the CTA ahead of dense metrics without collapsing the approved tablet header treatment.
- [x] 2.7 Refine the `768px`-`860px` tablet-portrait bridge so the hero and audience sections feel tablet-scaled, with a restrained action track and denser `3 x 2` grids, instead of feeling like oversized phone layouts.
- [x] 2.8 Add a section-qualified summary-module tablet override through `1119px` so the homepage summary cards collapse to two columns and drop the desktop equal-height assumption.
- [x] 2.9 Add a `861px`-`1119px` wide-tablet bridge and move the landing small-desktop onset to `1120px` so header controls, hero density, summary cards, and downstream section grids switch together instead of splitting across `1023px` / `1024px`.
- [x] 2.10 Add a `700px`-`767px` large-phone bridge so homepage content grids condense to two columns before tablet mode begins.
- [x] 2.11 Add a `<=320px` hero-title micro-adjustment so the compact-phone headline regains a safe right gutter.
- [x] 2.12 Make the `861px`-`1119px` hero track mildly fluid so the wide-tablet layout stays visually balanced near `1119px`.

## 3. Rebuild and verification

- [x] 3.1 Rebuild the site and run the narrowest useful landing-page verification command for the new phone-width rules.
- [x] 3.2 Re-run headless mobile Playwright captures at `390px` width and `320x568` compact-phone size to confirm the homepage no longer overflows horizontally and keeps the primary CTA near the first screen.
- [x] 3.3 Re-run headless mobile Playwright captures at `320x568`, `360x640`, and `390x844` to confirm the compact-phone gutter alignment and the absence of a breakpoint-order jump.
- [x] 3.4 Re-run headless Playwright captures at `767px`, `768px`, and `769px` widths to confirm the tablet-portrait bridge removes the breakpoint jump without regressing the tablet header controls.
- [x] 3.5 Re-run headless Playwright captures at `768px` and `860px` widths to confirm the refined tablet-portrait layout keeps a restrained CTA track plus denser `3 x 2` metric and audience grids.
- [x] 3.6 Re-run a headless Playwright capture around `1024px` width to confirm the homepage summary cards render in two columns instead of four.
- [x] 3.7 Re-run headless boundary captures at `860px`, `861px`, `1023px`, `1024px`, and `1120px` to confirm the new wide-tablet bridge removes the hybrid state and that desktop onset now starts together at `1120px`.
- [x] 3.8 Re-run headless breakpoint captures at `320px`, `700px`, `767px`, `861px`, and `1119px` to confirm the title gutter, large-phone density bridge, and fluid wide-tablet hero track all behave as intended.
