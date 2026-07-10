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
- **WHEN** the English landing homepage renders at phone widths up to `767px`
- **THEN** `.section-summary-modules .summary-grid` uses a single-column layout
- **THEN** the summary cards remain readable without clipping or horizontal scrolling

#### Scenario: Hero CTA appears before dense metrics on phones
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** the primary hero CTA block appears before the hero metric grid
- **THEN** the hero metric grid condenses to a phone-appropriate multi-row layout

#### Scenario: Phone audience cards keep dense readable layout
- **WHEN** the landing homepage renders at phone widths up to `767px`
- **THEN** the stakeholder cards render in a denser two-column mobile grid
- **THEN** the cards no longer rely on fixed desktop-width sizing that forces overflow or excessive scroll depth

#### Scenario: Compact phones keep the CTA and edition card readable
- **WHEN** the landing homepage renders at compact phone widths up to `360px`
- **THEN** the supporting copy, primary CTA, and hero metric grid stay on one inset content track, with the CTA still appearing before the dense metric grid
- **THEN** the primary hero CTA remains near the first screen by using tighter spacing without switching to a separate hero reading order from nearby phone widths
- **THEN** the edition card keeps a compact inline text-plus-cover layout that avoids excessive empty vertical space in the narrow viewport
