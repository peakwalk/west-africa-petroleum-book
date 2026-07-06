## ADDED Requirements

### Requirement: Homepage summary-modules row MUST match the approved four-card closing reference
The generated English homepage SHALL render its closing summary-modules section as a four-card reference row with the approved card hierarchy, list styling, and visible action links, rather than the prior equal-width informational cards without CTAs.

#### Scenario: Desktop layout follows the approved card composition
- **WHEN** the English homepage renders on desktop widths
- **THEN** the summary row renders four cards for latest updates, current edition, topics covered, and future development
- **THEN** the current-edition card is visually wider than the other cards
- **THEN** the latest-updates and topics-covered lists render green checkmark-style markers rather than plain bullets
- **THEN** the latest updates, topics covered, and future development cards each render a visible action link at the bottom

#### Scenario: Summary routing remains internal and functional
- **WHEN** a user activates a summary-card action link
- **THEN** `View all updates` and `Learn more` route to existing internal chapter-library destinations
- **THEN** `View all topics` routes to the existing homepage topics anchor
- **THEN** no new backend or placeholder route is required for this visual refresh

#### Scenario: Narrow viewports keep the summary cards usable
- **WHEN** the homepage renders on tablet or mobile widths
- **THEN** the summary cards continue to reflow through the existing responsive grid fallbacks
- **THEN** the current-edition cover image remains visible without clipping
- **THEN** list items and CTA labels remain readable at narrower widths
