## ADDED Requirements

### Requirement: Public asset build excludes source-only image backups
The site build SHALL not copy source-only image backups into either public asset tree when no runtime surface references them.

#### Scenario: Source-only images stay out of copied public trees
- **WHEN** `npm run build:site` completes
- **THEN** `public/assets/images/upstream-atlas-hero-book.png` does not exist
- **AND** `public/assets/images/prototype-hero-graywhite-left.png` does not exist
- **AND** `public/assets/images/prototype-hero-graywhite-right.png` does not exist
- **AND** the same three files do not exist under `public/fr/assets/images/`

### Requirement: French public tree excludes English-homepage-only assets
The site build SHALL not copy English-homepage-only assets into `public/fr/assets/` when the French output tree has no runtime references to them.

#### Scenario: French tree omits English-homepage-only assets
- **WHEN** `npm run build:site` completes
- **THEN** `public/fr/assets/images/upstream-atlas-hero-book.webp` does not exist
- **AND** `public/fr/assets/images/homepage-west-africa-map-panel.svg` does not exist
- **AND** the cropped WebP icon set under `public/fr/assets/icons/homepage-cropped/` does not exist

### Requirement: English root public tree excludes unreferenced icon groups
The site build SHALL not copy icon files into the English root public tree when the generated English pages inline or avoid those assets entirely.

#### Scenario: English root omits unreferenced icon groups
- **WHEN** `npm run build:site` completes
- **THEN** `public/assets/icons/country-flags.svg` does not exist
- **AND** the `public/assets/icons/homepage/` directory does not exist
- **AND** the `public/assets/icons/stakeholders/` directory does not exist
- **AND** the `public/assets/icons/topics/` directory does not exist
