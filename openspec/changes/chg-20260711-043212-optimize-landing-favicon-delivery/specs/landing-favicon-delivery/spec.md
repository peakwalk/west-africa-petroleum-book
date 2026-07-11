## ADDED Requirements

### Requirement: Landing shell uses split favicon delivery
Landing pages SHALL use a small dedicated PNG for browser favicon delivery and a separate larger PNG for Apple touch icon delivery instead of reusing the oversized shared favicon asset for all icon relationships.

#### Scenario: Landing homepage uses the small favicon and separate touch icon
- **WHEN** the English landing homepage renders its `<head>`
- **THEN** `rel="icon"` references `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="shortcut icon"` references `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="apple-touch-icon"` references `assets/images/upstream-atlas-apple-touch-icon.png`
- **AND** the landing homepage head does not reference `assets/images/upstream-atlas-favicon.png`

#### Scenario: French landing shell keeps the same split favicon contract
- **WHEN** the French landing homepage renders its `<head>`
- **THEN** `rel="icon"` references `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="shortcut icon"` references `assets/images/upstream-atlas-favicon-32.png`
- **AND** `rel="apple-touch-icon"` references `assets/images/upstream-atlas-apple-touch-icon.png`
