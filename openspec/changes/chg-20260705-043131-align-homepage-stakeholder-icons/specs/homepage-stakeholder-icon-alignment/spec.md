## ADDED Requirements

### Requirement: Homepage stakeholder cards MUST render the imported stakeholder source set with stable raster geometry
The homepage SHALL render the six stakeholder cards with repo-owned PNG icons imported from the user-supplied stakeholder source package, preserving that source set's silhouettes, single-color line treatment, and rendered visible bounds closely enough that the card row no longer depends on large CSS compensation to appear aligned.

#### Scenario: Imported source silhouettes replace the mismatched icon set
- **WHEN** the homepage stakeholder cards render on desktop
- **THEN** each card uses the imported repo-owned PNG asset for its stakeholder type instead of the currently mismatched silhouette
- **THEN** the icon treatment remains a single-color blue line drawing without accent-color dots or duotone details

#### Scenario: Fixed-width card boxes preserve stable icon alignment at doubled display size
- **WHEN** the stakeholder PNG assets are rendered inside the fixed `120px`-wide card layout
- **THEN** their visible bounds remain stable enough that only minor optical size adjustments are needed per card
- **THEN** the displayed icon size is doubled relative to the previous imported-asset CSS baseline instead of staying at the smaller placeholder scale
- **THEN** the six rendered icon centers land on the same horizontal line
- **THEN** icon alignment does not rely on large whitespace differences hidden inside the PNG canvases

#### Scenario: Geometry regression catches visible-bound drift
- **WHEN** stakeholder PNG assets are changed in the repo
- **THEN** focused verification inspects and trims each asset at its fixed pixel size
- **THEN** the verification fails if an icon's visible bounding box drifts away from the imported source baseline
