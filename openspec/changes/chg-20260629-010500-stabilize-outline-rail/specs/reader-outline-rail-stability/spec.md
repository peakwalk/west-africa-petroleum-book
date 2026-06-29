## ADDED Requirements

### Requirement: Shared Page Variant Classification
The reader SHALL derive desktop page-variant flags from one shared source so the initial boot pass and the hydrated pass apply the same preserve-outline-rail decision for a given pathname.

#### Scenario: Preserved rail page during boot and hydration
- **WHEN** a pathname matches an explicitly preserved outline-rail page
- **THEN** the initial page boot logic and the hydrated reader logic MUST both mark the page as preserving the desktop outline rail

#### Scenario: Non-preserved chapter page during boot and hydration
- **WHEN** a pathname does not match an explicitly preserved outline-rail page
- **THEN** the initial page boot logic and the hydrated reader logic MUST both leave preserved-rail classification disabled

### Requirement: Runtime Empty Outline Regression Guard
Site validation SHALL fail when a real chapter page would render with no visible runtime outline content and no intentional preserved desktop rail.

#### Scenario: Real chapter page would lose outline and preserved rail
- **WHEN** site validation simulates runtime outline visibility for a non-redirect chapter page and finds no visible headings, figures, tables, or formulas
- **THEN** validation MUST fail unless that page is explicitly classified to preserve the desktop outline rail

### Requirement: Figure Caption Fallback
The reader SHALL continue annotating figure cards when an image block has a `Figure N`-style alt label and is followed by a short adjacent caption paragraph, even if the paragraph does not repeat the full `Figure N ...` caption format.

#### Scenario: Alt label and short adjacent caption
- **WHEN** the reader finds an image block whose alt text identifies a figure number and the next paragraph is a short caption-like label
- **THEN** the reader MUST promote that image block and paragraph into a figure card for outline and figure-link behavior
