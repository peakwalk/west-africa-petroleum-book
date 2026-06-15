## ADDED Requirements

### Requirement: Locale-aware DOCX chapter extraction
Parity validation MUST support language-specific chapter markers and anchor rules so that each edition can be extracted from its own DOCX manuscript. French extraction MUST NOT depend on English-only `Chapter N:` markers.

#### Scenario: French chapter detection uses French chapter rules
- **WHEN** the French parity command extracts chapter boundaries from the French DOCX
- **THEN** it identifies all expected French chapters and front/back matter sections without relying on English chapter-marker regexes

#### Scenario: Edition-specific anchor rules are configurable
- **WHEN** a parity command resolves start or end anchors for an edition
- **THEN** the command reads that edition's chapter-title and anchor configuration from edition-aware validation inputs

### Requirement: Edition-scoped figure validation
Figure inventory, manifest generation, and figure-validation commands MUST run against the manuscript, summary, chapter tree, and figure root of the targeted edition. A failing French figure check MUST identify French assets and French chapter paths in its report.

#### Scenario: Figure validation targets the French source tree
- **WHEN** the French figure-validation command runs
- **THEN** it reads the French summary and French chapter directory and reports against the French figure-manifest

#### Scenario: Validation reports edition-specific paths
- **WHEN** an edition-scoped figure or parity check fails
- **THEN** the output identifies the failing edition and the locale-specific chapter or figure paths involved

#### Scenario: French figure inventory supports localized chapter and index formats
- **WHEN** the French DOCX uses `Chapitre N` markers and the French figure index uses `Figure N :` captions
- **THEN** the inventory and coverage checks still map each French figure number to the correct French chapter path

### Requirement: Dual-edition release gating
Site verification and Pages publishing MUST fail if either the English or French edition fails to build or validate. A successful release MUST therefore mean both editions passed their required parity, figure, and render checks.

#### Scenario: English success plus French failure blocks release
- **WHEN** the English edition passes but the French edition fails parity, figure, or render checks
- **THEN** the top-level site verification and publish workflow fail

#### Scenario: Both editions passing allows release
- **WHEN** both editions pass the required build and validation commands
- **THEN** the top-level verification and publish workflow succeed
