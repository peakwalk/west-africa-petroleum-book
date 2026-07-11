## ADDED Requirements

### Requirement: English homepage current-edition cover uses optimized non-critical delivery
The English landing homepage SHALL render the current-edition cover card from the repo-owned optimized WebP cover asset and SHALL mark that image as non-critical so it does not compete with the homepage hero for initial loading.

#### Scenario: English homepage cover card uses optimized WebP
- **WHEN** the English landing homepage renders the current-edition summary card
- **THEN** the card image references `assets/images/upstream-atlas-hero-book.webp`
- **AND** the card image markup includes `loading="lazy"`
- **AND** the card image markup includes `decoding="async"`
- **AND** the generated homepage does not reference `assets/images/upstream-atlas-hero-book.png` for that card
