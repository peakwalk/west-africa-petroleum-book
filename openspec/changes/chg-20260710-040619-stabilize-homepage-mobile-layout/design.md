## Context

The landing homepage already contains the correct structural markup for a mobile menu and a compact brand mark, but the narrow-width styles still behaved like a desktop-first page in several key places. At `390px`, the header kept the desktop navigation visible, `decision-strip` kept its two-column desktop grid, and the English summary row kept its four-column desktop layout. At `320x568`, the hero metrics sat above the CTA, the compact brand hit area stayed undersized, and the stakeholder / summary modules still carried desktop density. At `768x1024`, the page entered a mixed tablet/mobile state where the compact controls remained active but the hero reverted to placing the CTA after the metrics. After the first tablet-portrait bridge landed, the same `768x1024` review still felt off because the page read like a scaled-up phone layout rather than a portrait tablet layout. A later breakpoint audit around `1023px` and `1024px` showed a second boundary problem: tablet header controls and compact logo treatment still persisted, but some hero and summary behaviors had already drifted into desktop timing, so the page no longer changed density as one coherent system.

The concrete evidence from headless Playwright captures was:

- `390px`: `document.documentElement.scrollWidth` expanded to `477px`
- `390px`: `.decision-strip-inner` and `.decision-strip-copy` still resolved to two columns
- `390px`: `.section-summary-modules .summary-grid` still resolved to four columns
- `320x568`: the primary hero CTA sat far below the first screen
- `320x568`: the compact brand hit area rendered at roughly `32x44`, below the desired touch-target size
- `768x1024`: the hero CTA shrank to an inline-width button after the metric grid instead of staying on the narrow reading track
- `768x1024` after the first bridge: the hero CTA bars stretched almost the full content width, the hero metrics still dominated the first screen, and the audience cards sat in a sparse two-column grid with a large empty center gap
- `~1024px` width in the summary module review: `Latest Updates`, `Current Edition`, `Topics Covered`, and `Future Development` still rendered four-up because the tablet override used a weaker selector than the desktop `.section-summary-modules .summary-grid` rule
- `1023px`: mobile/tablet header controls were still active, but the hero CTA track had already collapsed back toward a desktop-like inline action rhythm
- `1024px`: desktop navigation and denser multi-column sections resumed, but the summary row still kept the tablet two-column treatment, proving the boundary between tablet and desktop had split across different modules
- `320px`: the compact-phone hero no longer overflowed, but the title still reached too close to the right viewport edge
- `767px`: the upper phone breakpoint stayed visually sparse because countries, topics, and summary modules were still single-column one pixel before tablet mode
- `1119px`: the wide-tablet hero kept the right reading order, but the fixed action/content track started to feel visibly left-heavy near the desktop cutoff

The supplied header reference adds one more concrete constraint: the narrow header should read as a left-aligned compact mark plus a right-aligned control group composed of a language pill, a circular contact button, and a menu pill. The existing landing CSS already contained `.header-contact-link`, so the header reference could be matched by wiring that missing control into the generated shell and tightening the phone breakpoint behavior instead of inventing a new pattern.

The repository also expects landing-page stylesheets to stay under reviewable size limits, so the final solution needs to keep mobile logic maintainable instead of continuing to grow a single catch-all responsive file.

## Goals / Non-Goals

**Goals:**
- Remove horizontal overflow from the landing homepage at phone widths.
- Activate the existing mobile header navigation treatment instead of leaving the desktop navigation visible on phones.
- Align the phone header control group to the supplied reference, including a dedicated contact button and no overlapping brand text.
- Keep the primary hero CTA above the metric grid at phone widths, keep it near the first screen on compact phones, and avoid a separate `<=360px` hero reading order.
- Keep the hero CTA ahead of the metric grid through the `768px` to `860px` tablet-portrait transition so the page does not jump into a mixed state at the mobile/tablet breakpoint.
- Keep the landing layout coherent through `861px` to `1119px` so header controls, hero density, and section grids still read as one tablet system before desktop starts.
- Stack the `decision-strip` container cleanly at phone widths while keeping its stakeholder cards dense enough to avoid an excessively tall section.
- Keep the English summary section readable at phone widths without fixed desktop card heights.
- Make desktop onset explicit at `1120px` so navigation, logo spacing, hero density, and section grids switch together.
- Add regression checks that fail if these phone-width overrides disappear again.

**Non-Goals:**
- Redesign the desktop or tablet landing experience.
- Change homepage copy, routes, or section ordering.
- Rebuild the French compatibility homepage body structure beyond shared mobile CSS effects.
- Revisit footer layout unless the mobile regression evidence shows it is still overflowing.

## Decisions

### Decision: Keep shared phone primitives in `landing.responsive-mobile.css` and move homepage-only phone rules into a dedicated partial
The markup already exposes the necessary mobile header controls and section wrappers. The durable fix is to keep shared header / generic phone primitives in `assets/css/landing.responsive-mobile.css`, but move homepage-specific phone behavior into `assets/css/landing.responsive-mobile-homepage.css` so the repository's stylesheet size guidance is still respected.

Alternatives considered:
- Patch generated `public/*.html` directly. Rejected because generated files are not the source of truth and would be overwritten on the next site build.
- Keep every new rule in one growing responsive file. Rejected because `landing.responsive-mobile.css` would exceed the repository's reviewable size limit.

### Decision: Match selector specificity for the summary grid override
The desktop summary layout comes from `.section-summary-modules .summary-grid`. The phone override must use the same section-qualified selector, not plain `.summary-grid`, otherwise the desktop rule keeps winning despite source order.

Alternatives considered:
- Add `!important` to the mobile grid rule. Rejected because matching the existing selector specificity is cleaner and easier to maintain.

### Decision: Reuse the tablet mobile-menu display pattern on phones
The tablet stylesheet already hides `.primary-nav` and reveals `.header-actions` plus `.mobile-nav-menu`. The phone breakpoint should intentionally follow the same behavior rather than inventing a third navigation mode.

Alternatives considered:
- Keep the desktop navigation visible and only shrink spacing further. Rejected because the current phone capture already shows the links crowding the header and contributing to layout instability.

### Decision: Reuse the existing header contact-button styling and the existing mail glyph
The landing styles already define `.header-contact-link`, and the reader toolbar already ships a mail glyph that matches the project's line-icon language. The narrowest fix is to render that contact link in `scripts/shared/landing-shell.mjs`, hide the brand reference copy on phones, and let the mobile breakpoint size the three right-side controls as a coherent action group.

Alternatives considered:
- Add a new mobile-only text contact pill. Rejected because the reference clearly uses a circular icon button and the header width is tighter than the desktop text CTA pattern.
- Keep the contact action inside the slide-down menu only. Rejected because the supplied reference calls for an immediately visible contact shortcut in the top row.

### Decision: Reflow the hero by CSS instead of changing homepage markup order
The hero copy block already has a stable DOM structure. On phones, the least risky way to prioritize the CTA is to turn `.hero-copy-block-v2` into a flex column and keep the supporting copy, CTA, and metric grid on one reading track, with the CTA block appearing before the metric grid. At compact-phone widths, the durable adjustment is tighter width/gap control on that same track rather than introducing a second hero ordering model.

Alternatives considered:
- Rewrite the homepage markup order in `scripts/shared/homepage-content.mjs`. Rejected because desktop and tablet layouts already read correctly from the current DOM order.

### Decision: Smooth the compact-phone breakpoint instead of forking a second `<=360px` mobile template
The first phone fix removed overflow, but follow-up `320x568` / `360x640` / `390x844` captures showed a new breakpoint jump: `390px` kept the copy before the CTA while `360px` switched to a CTA-first hero, `320px` let the copy/stat blocks extend farther right than the CTA, the mobile menu panel used asymmetric gutters, and the compact edition card became too empty when its cover stacked below the text. The durable fix is to keep `320px` through `390px` on the same hero reading order and inset content track, align `.mobile-nav-panel` to that same gutter system, and preserve a compact inline edition-card layout.

Alternatives considered:
- Keep the `<=360px` special hero ordering and stacked edition cover. Rejected because it created a visible structural jump between nearby phone widths and wasted vertical space in the summary section.

### Decision: Add a narrow tablet-portrait bridge instead of moving the global tablet breakpoint
The `768px` breakpoint already carries the approved tablet header/logo treatment. The regression is not that the tablet breakpoint exists, but that the hero falls back to desktop-like ordering as soon as that breakpoint activates. The least risky fix is a `768px` through `860px` override in `landing.responsive-tablet.css` that keeps the tablet header treatment intact while restoring a vertical hero reading track with the CTA before the metric grid.

Alternatives considered:
- Move the entire mobile breakpoint from `767px` to `860px`. Rejected because it would unnecessarily collapse the approved tablet header layout and other tablet grids into the phone presentation.
- Rewrite homepage DOM order for every width. Rejected because desktop and wider tablet layouts already rely on the current markup order and only the narrow tablet-portrait range needs help.

### Decision: Make the tablet-portrait bridge feel tablet-scaled instead of phone-scaled
The first bridge solved the ordering bug, but the visual review showed that simply reusing phone-like full-width CTA bars and a sparse two-column stakeholder layout still looked wrong at `768x1024`. The refined tablet-portrait treatment should keep the vertical hero reading order, but on a narrower content track with medium-width CTA bars, a denser `3 x 2` metric grid, and a denser `3 x 2` stakeholder grid that fills the available width more evenly.

Alternatives considered:
- Keep the full-width phone-style CTA bars on portrait tablets. Rejected because they made the hero feel oversized and pushed too much weight into the first screen.
- Keep the two-column stakeholder layout on portrait tablets. Rejected because the fixed-width cards left a large empty center gap and made the section feel under-designed.

### Decision: Add a wide-tablet bridge from `861px` through `1119px` and move desktop onset to `1120px`
The `1023px` / `1024px` audit showed that the breakpoint model was still splitting the page into incompatible states. The least disruptive fix is to keep the compact tablet header treatment active through `1119px`, add a second tablet bridge for `861px` through `1119px` that preserves tablet-density hero/actions/metrics plus `3 x 2` audience cards, and move the small-desktop header/nav onset to `1120px` so the true desktop layout begins as one coordinated transition.

Alternatives considered:
- Keep the existing `1024px` desktop onset and patch only the hero CTA width. Rejected because the audit showed multiple sections changing density at different widths, not just the hero action row.
- Force only the summary row back to desktop at `1024px`. Rejected because that would preserve the inconsistent boundary instead of removing it.

### Decision: Add a large-phone bridge from `700px` through `767px`
The sixth audit found that the last phone breakpoint still looked under-dense even though it was technically stable. The smallest fix is to leave the compact-phone header and hero behavior untouched, but allow the homepage content grids to shift into two columns from `700px` through `767px`. That trims excessive vertical whitespace without forcing the tablet header treatment to start early.

Alternatives considered:
- Leave all phone widths single-column through `767px`. Rejected because the `767px` capture looked notably sparser than the immediately adjacent `768px` tablet view.
- Move the full tablet breakpoint down below `768px`. Rejected because that would re-open the approved tablet header cutover.

### Decision: Add a `<=320px` hero-title micro-adjustment
The compact-phone hero track was mostly fixed, but the latest audit still measured a negative right gap for the title at `320px`. The narrowest fix is a tiny title-size and line-length adjustment only at `<=320px`, leaving the rest of the compact-phone copy/CTA/stat track intact.

Alternatives considered:
- Shrink the title for the full `<=360px` range. Rejected because `360px` was already landing on an acceptable right gutter.
- Re-tighten the entire compact-phone content track. Rejected because the CTA, copy, and stat blocks were already aligned correctly.

### Decision: Let the wide-tablet hero track grow slightly with the viewport
The `861px` through `1119px` bridge solved the mixed-state bug, but a fixed `33rem` action track and fixed content caps left the hero visually left-weighted near `1119px`. The refinement is to keep the same vertical tablet reading order while making the copy, action, and stat tracks mildly fluid with `clamp(...)`, so the wide-tablet hero scales with available width before the true desktop switch at `1120px`.

Alternatives considered:
- Keep the fixed widths through `1119px`. Rejected because the audit still showed an obvious balance issue near the upper tablet bound.
- Switch back to a desktop-style inline CTA rhythm earlier than `1120px`. Rejected because that would reintroduce the hybrid-state behavior this change set is removing.

### Decision: Use a section-qualified summary-grid override through `1119px`
The summary module review showed a different breakpoint bug: the tablet stylesheet already tried to move `.summary-grid` to two columns, but the desktop layout came from `.section-summary-modules .summary-grid`, so the weaker tablet selector lost on specificity and the cards stayed four-up through `1024px`. Once desktop onset moves to `1120px`, the narrowest fix is a section-qualified tablet override through `1119px` that explicitly sets the summary grid to two columns, removes the fixed desktop min-height assumption, and lets the cards align to their content.

Alternatives considered:
- Leave the generic `.summary-grid` tablet rule in place and rely on source order. Rejected because the desktop selector is more specific and would keep winning.
- Force the two-column tablet layout with `!important`. Rejected because matching selector specificity is cleaner and easier to maintain.

### Decision: Trade single-column audience cards for a denser two-column phone grid
The desktop stakeholder row cannot stay six-up, but collapsing it to one card per row makes the mobile section too tall. A two-column phone grid with flexible card sizing preserves readability without pushing the rest of the page unnecessarily far down.

Alternatives considered:
- Keep a one-column phone stack. Rejected because it increases scroll depth without improving comprehension.

## Risks / Trade-offs

- [Narrow-width selector updates could accidentally affect wider tablet layouts] -> Keep phone rules inside `@media (max-width: 767px)`, scope the portrait-tablet bridge to `@media (min-width: 768px) and (max-width: 860px)`, and scope the wide-tablet bridge to `@media (min-width: 861px) and (max-width: 1119px)` so each tablet band stays explicit.
- [Summary grid fix could unintentionally change French compatibility sections] -> Scope the single-column override to `.section-summary-modules .summary-grid`, which only targets the English summary row.
- [Header control changes could hide navigation entirely if the menu display rules are incomplete] -> Extend verification to assert the phone header block contains both the desktop-nav hide rule and the mobile-control show rules.
- [CTA prioritization could accidentally hide useful hero context] -> Keep the hero copy visible on all widths; compact phones only tighten spacing and gutters instead of switching to a different hero template.
- [Moving desktop onset could delay desirable desktop density on smaller landscape tablets] -> Verify the boundary explicitly at `860px`, `861px`, `1023px`, `1024px`, and `1120px` so the new onset still feels intentional on every transition point.
