## ADDED Requirements

### Requirement: English hero arrow asset is published
The static-site build SHALL publish `assets/icons/homepage/hero-arrow.svg` to `public/assets/icons/homepage/hero-arrow.svg`.

#### Scenario: English homepage asset build
- **WHEN** the static site is built
- **THEN** `public/assets/icons/homepage/hero-arrow.svg` exists
- **AND** the generated English homepage's hero-button CSS can load the referenced asset without a 404

### Requirement: Asset delivery remains edition-scoped
The build SHALL publish the hero arrow only in the English public asset tree, and SHALL preserve the French public tree's absence of that standalone homepage asset.

#### Scenario: French build output remains selective
- **WHEN** the static site is built
- **THEN** `public/fr/assets/icons/homepage/hero-arrow.svg` does not exist
- **AND** French homepage output and navigation remain unchanged
