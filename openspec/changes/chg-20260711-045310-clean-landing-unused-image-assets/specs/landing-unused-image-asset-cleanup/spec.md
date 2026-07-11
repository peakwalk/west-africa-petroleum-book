## ADDED Requirements

### Requirement: Landing source tree excludes retired historical image variants
The repository SHALL keep a defined set of retired landing image variants out of the active source tree so they are not republished by the site build.

#### Scenario: Retired landing source assets stay deleted
- **WHEN** the landing source assets are inspected
- **THEN** the following files do not exist under `assets/images/`:
  - `cover.png`
  - `homepage-west-africa-map-panel.png`
  - `homepage-west-africa-map-panel.webp`
  - `homepage-west-africa-map-panel@2x.png`
  - `prototype-hero-cutout.png`
  - `prototype-hero-edge-left.png`
  - `prototype-hero-edge-right.png`
  - `prototype-hero-grayscale-left.png`
  - `prototype-hero-grayscale-right.png`
  - `prototype-hero-overlay.png`
  - `upstream-atlas-hero-v2-photo.png`
  - `upstream-atlas-logo.png`
  - `upstream-atlas-nav-logo.png`

### Requirement: Landing builds do not republish retired historical image variants
The landing site build SHALL not copy the retired landing image variants into the generated English or French public asset trees.

#### Scenario: Built landing asset trees exclude retired images
- **WHEN** `npm run build:site` completes
- **THEN** the retired image list is absent from `public/assets/images/`
- **AND** the same retired image list is absent from `public/fr/assets/images/`
