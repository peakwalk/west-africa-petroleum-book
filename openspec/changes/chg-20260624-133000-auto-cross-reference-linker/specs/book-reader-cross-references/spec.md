## ADDED Requirements

### Requirement: Reader body copy auto-links supported textual references
The `/book/` reader MUST automatically convert supported body-copy references into links after the reader enhancement layer has created the relevant in-page anchors.

#### Scenario: Figure and table references link to local anchors
- **WHEN** a body-copy paragraph contains `Figure N` or `Table N`
- **AND** the current page contains the corresponding `#figure-n` or `#table-n` anchor target
- **THEN** the textual reference is converted into a link to that local anchor

#### Scenario: Section references link to the current chapter heading
- **WHEN** a body-copy paragraph contains `Section X.Y`
- **AND** the current page contains a heading whose displayed numbering starts with `X.Y`
- **THEN** the textual reference is converted into a link to that heading anchor

#### Scenario: Chapter references link to published chapter routes
- **WHEN** a body-copy paragraph contains `Chapter N`
- **AND** the reader sidebar contains the published route for Chapter `N`
- **THEN** the textual reference is converted into a link to that chapter page

#### Scenario: Equation references link to numbered formula anchors
- **WHEN** a body-copy paragraph contains `Equation X.Y` or `Formula X.Y`
- **AND** the current page or the published chapter route for chapter `X` provides the corresponding `#formula-x-y` target contract
- **THEN** the textual reference is converted into a link to that numbered equation anchor

### Requirement: Auto-linking must avoid broken or duplicate links
The `/book/` reader MUST leave unresolved references as plain text and MUST NOT wrap references that are already inside links or inside generated figure, table, or formula card chrome.

#### Scenario: Missing target stays plain text
- **WHEN** a body-copy reference has no resolvable figure, table, section, or chapter target
- **THEN** the reader leaves the original text unchanged

#### Scenario: Existing linked or generated-card content is skipped
- **WHEN** a reference appears inside an existing `<a>` element or inside generated figure, table, or formula card markup
- **THEN** the reader does not wrap it again
