## ADDED Requirements

### Requirement: Landing source tree excludes unreferenced historical asset variants
The repository SHALL keep a defined set of unreferenced historical landing asset variants out of the active source tree while preserving the active graywhite book-theme assets.

#### Scenario: Unreferenced historical source assets stay deleted
- **WHEN** the landing source assets are inspected
- **THEN** the following files do not exist under `assets/images/`:
  - `homepage-cabo-verde-inset.svg`
  - `prototype-hero-dusk.webp`
  - `prototype-hero-night.webp`
  - `prototype-hero-sunset-right.webp`
  - `prototype-hero-sunset-source.webp`
  - `prototype-hero.jpg`
  - `upstream-atlas-hero-v2-photo-right-fade.webp`
  - `upstream-atlas-hero-v3-clean.webp`
  - `upstream-atlas-hero-v4-clean.webp`
  - `upstream-atlas-hero-v5-soft-left.webp`
  - `upstream-atlas-hero-v6-soft-left.webp`
  - `upstream-atlas-wordmark.png`
  - `west-africa-intelligence-overlay.svg`

### Requirement: Landing builds do not republish unreferenced historical asset variants
The landing site build SHALL not copy the unreferenced historical landing asset variants into the generated English or French public asset trees.

#### Scenario: Built landing asset trees exclude unreferenced variants
- **WHEN** `npm run build:site` completes
- **THEN** the unreferenced historical asset list is absent from `public/assets/images/`
- **AND** the same list is absent from `public/fr/assets/images/`
