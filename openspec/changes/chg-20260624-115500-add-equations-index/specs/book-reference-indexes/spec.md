## ADDED Requirements

### Requirement: Front matter MUST expose a numbered equation index
The web book MUST publish a dedicated `List of Equations` page in front matter for each edition. The page MUST appear immediately after `List of Tables` and MUST list only numbered equations that already participate in the reader's equation-navigation contract.

#### Scenario: English front matter inserts the equation index after tables
- **WHEN** the English summary and site are built
- **THEN** `chapters/list-of-equations.html` exists and is ordered after `chapters/list-of-tables.html`

#### Scenario: French front matter inserts the equation index after tables
- **WHEN** the French summary and site are built
- **THEN** `chapters/list-of-equations.html` exists and is ordered after `chapters/list-of-tables.html`

### Requirement: Equation index links MUST reuse stable numbered formula anchors
The equation index MUST link to the existing numbered formula anchors generated from `data-equation-label`, so there is only one canonical navigation target per numbered equation.

#### Scenario: Numbered equation links target formula anchors
- **WHEN** an equation appears in the index
- **THEN** its link points at the existing `#formula-<number>` anchor in the owning chapter

#### Scenario: Unnumbered formulas stay out of the equation index
- **WHEN** a formula block does not have a numbered equation label
- **THEN** it is not included in `List of Equations`
