## ADDED Requirements

### Requirement: Homepage cropped icon source tree excludes retired PNG variants
The repository SHALL keep the retired `assets/icons/homepage-cropped/*.png` variants out of the active source tree while continuing to serve the matching WebP icon set.

#### Scenario: Cropped icon PNG source files stay deleted
- **WHEN** the homepage cropped-icon source directory is inspected
- **THEN** the following files do not exist under `assets/icons/homepage-cropped/`:
  - `icon-audience-operators.png`
  - `icon-audience-policy.png`
  - `icon-audience-research.png`
  - `icon-exploration.png`
  - `icon-fiscal.png`
  - `icon-industry-monitoring.png`
  - `icon-intelligence.png`
  - `icon-production.png`
  - `icon-regulation.png`
  - `icon-research.png`

### Requirement: Landing builds do not republish cropped icon PNG variants
The landing site build SHALL not copy the retired cropped-icon PNG variants into the generated English or French public asset trees.

#### Scenario: Built cropped-icon asset trees exclude PNG variants
- **WHEN** `npm run build:site` completes
- **THEN** the retired cropped-icon PNG list is absent from `public/assets/icons/homepage-cropped/`
- **AND** the same PNG list is absent from `public/fr/assets/icons/homepage-cropped/`
