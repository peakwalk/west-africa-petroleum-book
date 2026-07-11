## ADDED Requirements

### Requirement: Root landing outputs stay out of source control

The repository MUST NOT keep tracked root-level landing HTML outputs that duplicate the deployed `public/` site surface.

#### Scenario: root landing outputs are cleaned from the repo

- **WHEN** the repository tree is inspected after the cleanup
- **THEN** `index.html` does not exist at the repository root
- **AND** `fr/index.html` does not exist in the repository root locale directory

### Requirement: Standalone landing generators default to the deployed output root

Standalone landing generation commands MUST write to the deployed output tree unless a caller explicitly overrides the destination.

#### Scenario: package aliases target the deployed output tree

- **WHEN** a contributor runs the package landing-generation aliases without extra flags
- **THEN** `build:index`, `build:legal`, and `build:chapters` target `public/`
- **AND** the generated landing pages continue to reference only `upstream-atlas-favicon-32.png`, `upstream-atlas-apple-touch-icon.png`, and `upstream-atlas-icon.png` as landing PNG assets
