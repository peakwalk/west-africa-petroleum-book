## ADDED Requirements

### Requirement: Landing pages use consistent web-sourced SVG icon assets outside hero stats
The generated landing pages SHALL keep the current `hero-stat-icon` assets unchanged while rendering the remaining visible icon surfaces from curated SVG assets sourced from one official web icon library.

#### Scenario: English homepage topic cards use SVG assets
- **WHEN** the English homepage is generated
- **THEN** each topic-reference card SHALL reference `/assets/icons/topics/*.svg` assets instead of `/assets/icons/topics/*.png`

#### Scenario: Shared non-hero landing icon surfaces use curated SVG assets
- **WHEN** the English homepage or French compatibility homepage is generated
- **THEN** stakeholder icons, search-scope icons, homepage feature icons, audience icons, country-signal icons, and control sprite icons SHALL resolve to curated SVG assets under the existing landing asset directories
