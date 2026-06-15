## ADDED Requirements

### Requirement: Shared edition registry
The build system MUST resolve every edition from one checked-in registry instead of hard-coded English paths. The registry MUST define the locale code, public route prefix, manuscript alias paths, Markdown source root, legal content root, figure root, and book config for each edition.

#### Scenario: Build scripts resolve the French edition from config
- **WHEN** a build or verification command targets the French edition
- **THEN** the command reads the French source root, manuscript aliases, and output prefix from the shared edition registry instead of hard-coded `src` or English manuscript paths

#### Scenario: New edition inputs remain additive
- **WHEN** the registry contains both `en` and `fr`
- **THEN** generator code uses the same script entrypoints for both editions and does not require a second copy of each build script

### Requirement: Mirrored source topology across editions
The French edition MUST mirror the English source topology for summary structure, chapter slugs, legal page keys, and figure numbering. User-facing titles and content MAY change by locale, but internal slugs and figure identifiers MUST stay aligned across editions.

#### Scenario: Chapter slugs are stable across locales
- **WHEN** the English and French chapter source trees are compared
- **THEN** each chapter file is addressable by the same slug path in both editions even though the rendered titles differ by language

#### Scenario: Figure numbers remain aligned across locales
- **WHEN** figure manifests are generated for both editions
- **THEN** the same figure number maps to the locale-specific caption and locale-specific asset set for that edition

### Requirement: Locale-scoped manuscript and figure assets
Each edition MUST use its own canonical DOCX/PDF aliases and its own figure-manifest and rendered figure assets. The French edition MUST NOT reuse the English figure-manifest or English text-replacement map as its source of truth.

#### Scenario: French figure rendering reads French manuscript aliases
- **WHEN** a French figure render or inventory command runs
- **THEN** it reads the French DOCX/PDF alias paths and writes or validates against the French figure root

#### Scenario: English text replacement is not applied to French figures
- **WHEN** a French figure contains native French chart or document labels
- **THEN** the render pipeline preserves the French labels unless the French edition defines its own replacement map

#### Scenario: French figure root is isolated from the English shared tree
- **WHEN** the French edition builds or validates figures
- **THEN** it uses a real `src-fr/images` root instead of a symlinked or shared `src/images` directory

#### Scenario: French published assets converge to French manuscript output
- **WHEN** a French figure asset is finalized for release
- **THEN** that asset is rendered from the French DOCX/PDF inputs for its figure kind rather than copied from the English published asset tree
