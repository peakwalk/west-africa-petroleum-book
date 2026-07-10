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
- [x] 2.13 Normalize the homepage search-field gutter across phone, tablet, and small-desktop widths so the input pill no longer reads edge-to-edge through the `768px`-`1200px` span.
- [x] 2.14 Convert the `861px`-`1119px` homepage search-scope chips to a fixed two-row grid so `1119px` wide tablets no longer leave a single orphan chip on the last row.
- [x] 2.15 Replace content-width search-scope chip wrapping with stable responsive grids: `2` columns on phone, `4` columns from large-phone through small-desktop, and the original single-row layout only once `1280px+` has enough width.
- [x] 2.16 Widen the `1120px`-`1279px` homepage search-scope grid so the longest chip labels return to a single line before the `1280px+` single-row desktop layout begins.
- [x] 2.17 Split the previous `700px`-`1119px` search-scope bridge into a `2`-column `700px`-`959px` layout and a widened `4`-column `960px`-`1279px` layout so tablet widths stop forcing internal chip-label wraps.
- [x] 2.18 Refine the `700px`-`959px` search-scope bridge into a centered `3`-column wrap so `700px` and `768px` feel denser while the last row stays visually balanced.
- [x] 2.19 Remove the now-obsolete overlapping search-scope media blocks so the final breakpoint logic reads as one phone block, one `3`-column bridge, and one widened `4`-column bridge.
- [x] 2.20 Widen the `700px`-`959px` `3`-column search-scope container so the chip group sits closer to the search-input width at the upper end of the bridge.
- [x] 2.21 Split the `700px`-`959px` search-scope bridge into `700px`-`767px` and `768px`-`959px` width rules so the chip group can follow the same side gutters as the search input on each side of the tablet breakpoint.
- [x] 2.22 Widen the `960px`-`1279px` `4`-column search-scope grid cap so wide tablets and near-desktop widths stop leaving an overly isolated chip block beneath the broader search input.
- [x] 2.23 Extend the `4`-column search-scope bridge through `1439px` and keep it on the same content width as the search input so the equal-width tablet/desktop block hands off to the single-row pills only at true wide-desktop widths.
- [x] 2.24 Move the remaining wide-desktop header, hero, and search-scope enhancements to `1600px+` so `1440px` no longer triggers a compound layout jump in the top landing sections.
- [x] 2.25 Remove the counterproductive `1600px+` hero/decision-strip downsizing overrides and delay the remaining header/search-scope wide-desktop handoff to `1680px` so `1600px` no longer introduces a new compound jump.
- [x] 2.26 Slightly widen the `861px`-`1119px` hero-title measure so wide tablets stop dropping `Reference` onto a third orphan line while preserving the single-column tablet hero treatment.

## 3. Rebuild and verification

- [x] 3.1 Rebuild the site and run the narrowest useful landing-page verification command for the new phone-width rules.
- [x] 3.2 Re-run headless mobile Playwright captures at `390px` width and `320x568` compact-phone size to confirm the homepage no longer overflows horizontally and keeps the primary CTA near the first screen.
- [x] 3.3 Re-run headless mobile Playwright captures at `320x568`, `360x640`, and `390x844` to confirm the compact-phone gutter alignment and the absence of a breakpoint-order jump.
- [x] 3.4 Re-run headless Playwright captures at `767px`, `768px`, and `769px` widths to confirm the tablet-portrait bridge removes the breakpoint jump without regressing the tablet header controls.
- [x] 3.5 Re-run headless Playwright captures at `768px` and `860px` widths to confirm the refined tablet-portrait layout keeps a restrained CTA track plus denser `3 x 2` metric and audience grids.
- [x] 3.6 Re-run a headless Playwright capture around `1024px` width to confirm the homepage summary cards render in two columns instead of four.
- [x] 3.7 Re-run headless boundary captures at `860px`, `861px`, `1023px`, `1024px`, and `1120px` to confirm the new wide-tablet bridge removes the hybrid state and that desktop onset now starts together at `1120px`.
- [x] 3.8 Re-run headless breakpoint captures at `320px`, `700px`, `767px`, `861px`, and `1119px` to confirm the title gutter, large-phone density bridge, and fluid wide-tablet hero track all behave as intended.
- [x] 3.9 Rebuild the site and re-run the narrowest useful homepage search-surface CSS assertions after the cross-breakpoint gutter normalization.
- [x] 3.10 Rebuild the site and re-run the narrowest useful wide-tablet search-scope CSS assertions after removing the `1119px` orphan chip row.
- [x] 3.11 Re-run headless search-scope captures at `320px`, `390px`, `700px`, `768px`, `1119px`, `1200px`, and `1280px` to confirm the responsive chip grids stay aligned until the single-row desktop layout fits again.
- [x] 3.12 Re-run headless search-scope captures at `1119px`, `1120px`, `1200px`, `1279px`, and `1280px` to confirm the widened small-desktop grid removes internal chip-label wrapping without losing centered gutters.
- [x] 3.13 Re-run headless search-scope captures at `700px`, `768px`, `959px`, `960px`, `1024px`, `1119px`, and `1280px` to confirm the new `2`-column / `4`-column breakpoint split removes tablet wrapping without reintroducing orphan rows or edge-to-edge gutters.
- [x] 3.14 Re-run headless search-scope captures at `700px`, `768px`, `959px`, and `960px` to confirm the centered `3`-column bridge keeps single-line labels while the last row stays centered across the breakpoint handoff.
- [x] 3.15 Re-run the landing CSS assertions after removing the superseded search-scope media blocks to confirm the simplified stylesheet still resolves to the same verified breakpoints.
- [x] 3.16 Re-run headless `700px`, `768px`, and `959px` search-scope captures after widening the `3`-column bridge to confirm the chip group moves closer to the search-input width without reintroducing label wraps.
- [x] 3.17 Re-run headless `700px`, `768px`, and `959px` search-scope captures after aligning the split bridge widths to the search-input gutters so the chip group and input share the same side margins without breaking the `3`-column labels.
- [x] 3.18 Re-run headless `960px`, `1024px`, `1119px`, and `1279px` search-scope captures after widening the `4`-column cap to confirm the wider tablet block reduces center-floating without reintroducing chip-label wraps or orphan rows.
- [x] 3.19 Re-run headless `1279px`, `1280px`, `1366px`, `1439px`, and `1440px` search-scope captures after moving the single-row handoff to wide desktop to confirm the breakpoint jump is smoothed without reintroducing chip-label wraps.
- [x] 3.20 Re-run headless `1439px`, `1440px`, and `1600px` landing captures after shifting the remaining wide-desktop enhancements so the header, hero stat rail, and search-scope no longer jump together at `1440px`.
- [x] 3.21 Re-run headless `1599px`, `1600px`, `1679px`, and `1680px` landing captures after removing the shrinking overrides and moving the last handoff to `1680px` so the wide-desktop transition stays monotonic and no longer changes multiple regions at `1600px`.
- [x] 3.22 Re-run headless `861px`, `959px`, `1119px`, and `1120px` landing captures after widening the wide-tablet hero-title measure to confirm the orphan line disappears before desktop onset without reintroducing the earlier breakpoint jump.
