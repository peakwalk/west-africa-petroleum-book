## ADDED Requirements

### Requirement: Homepage browse-by-topic surface MUST match the approved six-card topic reference
The generated English homepage SHALL render its browse-by-topic section as a compact six-card topical navigation strip with one visible section heading, rather than the prior large editorial heading plus ten-card information grid.

#### Scenario: Desktop layout follows the approved topic composition
- **WHEN** the English homepage renders on desktop widths
- **THEN** the section shows one visible heading reading `Browse by Topic`
- **THEN** the section renders exactly six topical cards for petroleum value chain, West African fiscal regimes, national oil companies, upstream operations, governance & regulation, and country analysis
- **THEN** each card shows a leading icon, topic title, concise supporting description, and an `Explore` link
- **THEN** the old large narrative heading is not visibly rendered in the section

#### Scenario: Topic routing remains unchanged
- **WHEN** a user activates one of the English homepage browse-by-topic cards
- **THEN** each card links to the existing corresponding chapter destination already used by the homepage generator
- **THEN** the destinations for petroleum value chain, West African fiscal regimes, national oil companies, upstream operations, governance & regulation, and country analysis remain unchanged by this visual redesign

#### Scenario: Narrow viewports and French fallback remain usable
- **WHEN** the homepage renders on tablet or mobile widths
- **THEN** the English topic cards reflow within the shared landing content width without clipping icons or link labels
- **THEN** the card copy remains readable at narrower widths
- **THEN** the French compatibility homepage keeps its separate compact topic fallback layout instead of adopting the English reference-grid class
