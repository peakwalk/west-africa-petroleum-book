## ADDED Requirements

### Requirement: Homepage white-surface sections MUST use a shared text-color hierarchy
The generated homepage SHALL use a consistent text-color hierarchy across its white-surface sections so headings, descriptive copy, metadata, and interactive text no longer rely on module-specific near-duplicate blues to communicate their role.

#### Scenario: Descriptive text is calmer than headings and links
- **WHEN** a user scans homepage white-surface sections such as the stakeholder strip, country grid, map overview, search surface, topic cards, and summary cards
- **THEN** section headings remain the strongest non-hero text in those sections
- **THEN** descriptive body copy renders in a calmer supporting text role than emphasized entity names or card headings
- **THEN** metadata such as dates, abbreviations, and helper labels render in a quieter role than descriptive body copy

#### Scenario: Similar text roles do not drift between adjacent modules
- **WHEN** two adjacent homepage modules use the same semantic text role on white surfaces
- **THEN** those roles share the same token or visual role assignment rather than separate hard-coded near-match blues
- **THEN** the page does not depend on arbitrary module-level color differences to create hierarchy

### Requirement: Homepage interactive text MUST share one consistent visual family on white surfaces
Homepage section links, card links, and chip-like interactive labels on white surfaces SHALL share one default interactive text role and one hover/focus-visible interactive role unless a stronger exception is explicitly required by the approved reference.

#### Scenario: White-surface CTAs share one default link baseline
- **WHEN** a user views `View All Countries`, country analysis links, topic card links, summary-card links, or search-scope chips
- **THEN** those interactive labels render from the same default interactive text family
- **THEN** they remain visually distinct from nearby descriptive copy

#### Scenario: White-surface hover states stay related without inventing new blues
- **WHEN** a user hovers or focuses a homepage white-surface text CTA
- **THEN** the hover or focus-visible state uses the shared interactive hover family instead of a module-specific one-off blue
- **THEN** the CTA remains recognizably part of the same homepage interaction system
