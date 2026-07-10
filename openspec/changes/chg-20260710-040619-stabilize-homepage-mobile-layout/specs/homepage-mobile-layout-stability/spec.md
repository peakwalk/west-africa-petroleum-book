## ADDED Requirements

### Requirement: Landing homepage MUST remain stable and action-prioritized at phone widths
The landing homepage SHALL avoid horizontal overflow at phone widths and SHALL prioritize the primary reading CTA by switching the shared header and homepage section grids to phone-appropriate layouts whenever the desktop layout would exceed the viewport.

#### Scenario: Phone header switches to compact navigation controls
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** the desktop `.primary-nav` is hidden
- **THEN** the existing `.header-actions` and `.mobile-nav-menu` controls are visible
- **THEN** the compact brand mark remains visible within the viewport without overlapping brand-reference copy
- **THEN** the header action row shows a dedicated contact icon button between the language switch and the menu control
- **THEN** compact phone menu panels align to the same inset content gutter as the rest of the narrow header controls

#### Scenario: Decision strip stacks on phones
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** `.decision-strip-inner` uses a single-column layout
- **THEN** `.decision-strip-copy` uses a single-column layout
- **THEN** the section no longer forces horizontal scrolling

#### Scenario: English summary modules stack on phones
- **WHEN** the English landing homepage renders at phone widths up to `699px`
- **THEN** `.section-summary-modules .summary-grid` uses a single-column layout
- **THEN** the summary cards remain readable without clipping or horizontal scrolling

#### Scenario: Large phones condense homepage content grids before tablet mode
- **WHEN** the landing homepage renders at widths from `700px` through `767px`
- **THEN** the compact phone header treatment remains active
- **THEN** the countries, topics, and summary modules condense into two-column grids
- **THEN** the page no longer keeps the sparse single-column content density all the way to the tablet breakpoint

#### Scenario: English summary modules condense on tablets
- **WHEN** the English landing homepage renders at widths from `768px` through `1119px`
- **THEN** `.section-summary-modules .summary-grid` uses a two-column layout
- **THEN** the summary cards no longer stay in the desktop four-column arrangement
- **THEN** the summary cards align to content-driven heights instead of being stretched by the desktop minimum-height assumption

#### Scenario: Hero CTA appears before dense metrics on phones
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** the primary hero CTA block appears before the hero metric grid
- **THEN** the hero metric grid condenses to a phone-appropriate multi-row layout

#### Scenario: Tablet portrait keeps the CTA ahead of dense metrics
- **WHEN** the landing homepage renders at tablet-portrait widths from `768px` through `860px`
- **THEN** the hero title, supporting copy, primary CTA, and hero metric grid stay on one vertical reading track
- **THEN** the primary hero CTA appears before the hero metric grid
- **THEN** the CTA stays on a restrained tablet-width action track instead of stretching across the entire content width like a phone-sized bar
- **THEN** the hero metric grid condenses into a denser `3 x 2` tablet-portrait layout
- **THEN** the audience stakeholder cards condense into a denser `3 x 2` tablet-portrait layout without leaving a large empty center gap

#### Scenario: Wide tablets keep one coherent tablet-density layout
- **WHEN** the landing homepage renders at widths from `861px` through `1119px`
- **THEN** the compact tablet header controls remain active instead of switching to desktop navigation
- **THEN** the hero title, supporting copy, primary CTA, and hero metric grid stay on one tablet-density reading track
- **THEN** the primary hero CTA remains a full-row tablet action, not an inline desktop-style button
- **THEN** the hero copy and action tracks can grow modestly with the viewport instead of staying locked to one fixed width
- **THEN** the hero metric grid and audience stakeholder cards stay in denser `3 x 2` tablet layouts
- **THEN** the topics, countries, and summary sections keep their two-column tablet grids

#### Scenario: Desktop layout resumes together at `1120px`
- **WHEN** the landing homepage renders at widths from `1120px` upward
- **THEN** the desktop `.primary-nav` is visible
- **THEN** the compact tablet header controls are no longer the primary navigation treatment
- **THEN** the desktop-density hero and section grids begin together instead of switching module-by-module around `1024px`

#### Scenario: Phone audience cards keep dense readable layout
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** the stakeholder cards render in a denser two-column mobile grid
- **THEN** the cards no longer rely on fixed desktop-width sizing that forces overflow or excessive scroll depth

#### Scenario: Compact phones keep the CTA and edition card readable
- **WHEN** the landing homepage renders at compact phone widths up to `360px`
- **THEN** the supporting copy, primary CTA, and hero metric grid stay on one inset content track, with the CTA still appearing before the dense metric grid
- **THEN** the primary hero CTA remains near the first screen by using tighter spacing without switching to a separate hero reading order from nearby phone widths
- **THEN** the edition card keeps a compact inline text-plus-cover layout that avoids excessive empty vertical space in the narrow viewport
- **THEN** the hero title regains a visible right gutter at `320px` instead of pressing against the viewport edge
