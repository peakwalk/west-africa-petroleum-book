## ADDED Requirements

### Requirement: Homepage west Africa map overview MUST match the approved west-coast reference composition
The English homepage SHALL render its map-overview module as the approved west-coast political reference composition, with a compact introductory text block on the left, a blue `Explore the Map` CTA, a Cape Verde inset, and a coastline-oriented West Africa political basemap on the right instead of the current abstract mainland polygon.

#### Scenario: Desktop layout follows the approved composition
- **WHEN** the English homepage renders on desktop
- **THEN** the map-overview module places the title/body/CTA in a narrow left column and the political map panel in the right column
- **THEN** the right column shows the Cape Verde inset and the west-coast political basemap rather than a generic clipped landmass
- **THEN** the map CTA uses the approved blue treatment for this module instead of the default orange primary button style

#### Scenario: Country hotspots preserve existing destinations
- **WHEN** a user activates a country hotspot from the map-overview panel
- **THEN** the destination matches the same country-analysis route used by that country's homepage card
- **THEN** keyboard focus and hover expose a visible hotspot affordance without replacing the approved reference artwork

#### Scenario: Country cards keep their flags in standalone homepage output
- **WHEN** the English homepage renders its country cards
- **THEN** the document includes the shared country-flag sprite definitions needed by those cards
- **THEN** each country-card flag references a local fragment ID such as `#nigeria` instead of an external `/assets/icons/country-flags.svg#...` URL

#### Scenario: Narrow viewports keep the panel legible
- **WHEN** the homepage renders on tablet or mobile widths
- **THEN** the map-overview copy and map panel stack without clipping the artwork or CTA
- **THEN** the political map image scales proportionally and hotspot routing remains available
