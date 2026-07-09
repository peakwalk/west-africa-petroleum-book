## ADDED Requirements

### Requirement: Homepage west Africa map overview MUST match the approved west-coast reference composition
The English homepage SHALL render its map-overview module as the approved west-coast political reference composition, with a compact introductory text block on the left, a blue `Explore the Map` CTA, and the user-supplied West Africa political SVG on the right, including the SVG's integrated Cape Verde inset and visible country flags.

#### Scenario: Desktop layout follows the approved composition
- **WHEN** the English homepage renders on desktop
- **THEN** the map-overview module places the title/body/CTA in a narrow left column and the political map panel in the right column
- **THEN** the right column shows the integrated Cape Verde inset, visible country flags, and the west-coast political basemap from the supplied SVG rather than a generic clipped landmass
- **THEN** the map CTA uses the approved blue treatment for this module instead of the default orange primary button style

#### Scenario: Country hotspots preserve existing destinations
- **WHEN** a user activates a country hotspot from the map-overview panel
- **THEN** the destination matches the same country-analysis route used by that country's homepage card
- **THEN** keyboard focus and hover expose a visible hotspot affordance while keeping each hotspot centered on the corresponding flag embedded in the supplied SVG

#### Scenario: Small west-coast states stay legible without obscuring borders
- **WHEN** the map-overview panel renders small or narrow west-coast states whose borders are too tight for an in-place flag
- **THEN** the panel MAY render that state's visible flag slightly offset from the border
- **THEN** the panel MUST keep a clear visual association back to the intended state, such as an internal anchor point plus a short leader line

#### Scenario: Country cards keep their flags in standalone homepage output
- **WHEN** the English homepage renders its country cards
- **THEN** the document includes the shared country-flag sprite definitions needed by those cards
- **THEN** each country-card flag references a local fragment ID such as `#nigeria` instead of an external `/assets/icons/country-flags.svg#...` URL

#### Scenario: Narrow viewports keep the panel legible
- **WHEN** the homepage renders on tablet or mobile widths
- **THEN** the map-overview copy and map panel stack without clipping the artwork or CTA
- **THEN** the political map image scales proportionally and hotspot routing remains available
