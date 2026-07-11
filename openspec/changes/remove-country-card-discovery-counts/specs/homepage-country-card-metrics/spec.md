## ADDED Requirements

### Requirement: Country cards present only an objective producing-field metric
The generated English homepage SHALL render all 16 country cards with exactly one country-summary metric: the country's producing-field count and its Producing Fields label. A country card MUST NOT render a discovery count, a Discoveries label, or any equivalent discovery metric.

#### Scenario: Generated country cards omit discovery counts
- **WHEN** the English homepage is generated
- **THEN** each of the 16 country-card metric lists contains one producing-field entry and no discovery metric entry

### Requirement: Country-card removal is scoped to country-card content
The system SHALL retain the existing country name, status, flag, ministry/NOC metadata, hydrocarbon information, country-analysis link, and producing-field count for every country card. The change MUST NOT remove discovery-related content outside country cards.

#### Scenario: Unrelated homepage discovery content is preserved
- **WHEN** the homepage is generated after the country-card change
- **THEN** country-card discovery metrics are absent while unrelated homepage discovery content remains unchanged

### Requirement: Country cards remain balanced and responsive
The country-card layout SHALL use one shared height and spacing treatment that leaves no discovery-row gap and keeps the country-analysis link usable. The desktop, tablet, and mobile grids MUST continue to render all country cards without clipping, overlap, or card-specific height overrides.

#### Scenario: Country cards render across target widths
- **WHEN** the generated homepage is inspected at desktop, tablet, and mobile viewport widths
- **THEN** all country cards remain visually balanced, their content is legible and reachable, and the responsive grid remains intact
