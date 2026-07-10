## Context

The landing homepage already contains the correct structural markup for a mobile menu and a compact brand mark, but the phone-width styles still behaved like a desktop-first page in several key places. At `390px`, the header kept the desktop navigation visible, `decision-strip` kept its two-column desktop grid, and the English summary row kept its four-column desktop layout. At `320x568`, the hero metrics sat above the CTA, the compact brand hit area stayed undersized, and the stakeholder / summary modules still carried desktop density.

The concrete evidence from headless Playwright captures was:

- `390px`: `document.documentElement.scrollWidth` expanded to `477px`
- `390px`: `.decision-strip-inner` and `.decision-strip-copy` still resolved to two columns
- `390px`: `.section-summary-modules .summary-grid` still resolved to four columns
- `320x568`: the primary hero CTA sat far below the first screen
- `320x568`: the compact brand hit area rendered at roughly `32x44`, below the desired touch-target size

The supplied header reference adds one more concrete constraint: the narrow header should read as a left-aligned compact mark plus a right-aligned control group composed of a language pill, a circular contact button, and a menu pill. The existing landing CSS already contained `.header-contact-link`, so the header reference could be matched by wiring that missing control into the generated shell and tightening the phone breakpoint behavior instead of inventing a new pattern.

The repository also expects landing-page stylesheets to stay under reviewable size limits, so the final solution needs to keep mobile logic maintainable instead of continuing to grow a single catch-all responsive file.

## Goals / Non-Goals

**Goals:**
- Remove horizontal overflow from the landing homepage at phone widths.
- Activate the existing mobile header navigation treatment instead of leaving the desktop navigation visible on phones.
- Align the phone header control group to the supplied reference, including a dedicated contact button and no overlapping brand text.
- Keep the primary hero CTA above the metric grid at phone widths, keep it near the first screen on compact phones, and avoid a separate `<=360px` hero reading order.
- Stack the `decision-strip` container cleanly at phone widths while keeping its stakeholder cards dense enough to avoid an excessively tall section.
- Keep the English summary section readable at phone widths without fixed desktop card heights.
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

### Decision: Trade single-column audience cards for a denser two-column phone grid
The desktop stakeholder row cannot stay six-up, but collapsing it to one card per row makes the mobile section too tall. A two-column phone grid with flexible card sizing preserves readability without pushing the rest of the page unnecessarily far down.

Alternatives considered:
- Keep a one-column phone stack. Rejected because it increases scroll depth without improving comprehension.

## Risks / Trade-offs

- [Phone-specific selector updates could accidentally affect tablet widths] -> Keep all new overrides inside `@media (max-width: 767px)` or narrower blocks, while preserving tablet behavior in `landing.responsive-tablet.css`.
- [Summary grid fix could unintentionally change French compatibility sections] -> Scope the single-column override to `.section-summary-modules .summary-grid`, which only targets the English summary row.
- [Header control changes could hide navigation entirely if the menu display rules are incomplete] -> Extend verification to assert the phone header block contains both the desktop-nav hide rule and the mobile-control show rules.
- [CTA prioritization could accidentally hide useful hero context] -> Keep the hero copy visible on all widths; compact phones only tighten spacing and gutters instead of switching to a different hero template.
