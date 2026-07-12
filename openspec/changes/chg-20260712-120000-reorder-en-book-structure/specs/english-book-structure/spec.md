## ADDED Requirements

### Requirement: Reordered English chapter sequence
The English edition SHALL list the data-management chapter immediately after Chapter 6 as Chapter 7. The former Chapters 7, 8, and 9 SHALL be displayed as Chapters 8, 9, and 10 respectively, while Chapters 5, 11, and 12 retain their existing display numbers.

#### Scenario: Reader follows the revised sequence
- **WHEN** a reader opens the English table of contents or chapter sidebar
- **THEN** it lists Chapters 5 through 12 in the order 5, 6, data management 7, petroleum fiscal regimes 8, West African fiscal regimes 9, socio-political determinants 10, 11, and 12

### Requirement: Part membership and labels remain coherent
The English edition SHALL retain Chapter 5 in Part II, label Part II as "Upstream Petroleum Operations and Development", and begin Part III with Chapter 8 under the label "Petroleum Fiscal, Commercial and Economic Framework".

#### Scenario: Every affected chapter has one part
- **WHEN** a reader views the English summary or generated chapter library
- **THEN** Chapter 5 through Chapter 7 appear in Part II and Chapter 8 through Chapter 12 appear in Part III

### Requirement: Numbered content and internal references stay aligned
The English chapter titles, numbered headings, manual table of contents, figure/table/equation index headings, and intentional prose chapter references SHALL use the revised chapter-number map. Links from manual indexes SHALL resolve to the matching generated chapter and heading.

#### Scenario: Reader follows an index heading link
- **WHEN** a reader selects an affected chapter or numbered-heading link from an English manual index
- **THEN** the link opens the chapter and heading whose displayed number matches the index

### Requirement: Chapter routes match display numbers and preserve legacy links
The English edition SHALL use canonical source paths and generated chapter URLs whose chapter numbers match the revised displayed numbers. The former URLs for the four renumbered chapters SHALL remain available as non-canonical redirect pages that preserve query strings and fragments.

#### Scenario: Canonical chapter URL is requested
- **WHEN** a reader opens a canonical URL for the data-management, fiscal-regime, West-African-fiscal-regime, or socio-political chapter
- **THEN** its filename number and visible chapter number match

#### Scenario: Former chapter URL is requested
- **WHEN** a reader opens a former URL for one of the four renumbered chapters with a query string or fragment
- **THEN** the redirect opens the matching canonical chapter and preserves the query string and fragment

### Requirement: English reference DOCX matches the revised sequence
The English source reference DOCX SHALL contain the data-management chapter immediately after Chapter 6 as Chapter 7, followed by the fiscal, West-African-fiscal, and socio-political chapters as Chapters 8, 9, and 10. The update SHALL be made directly to the DOCX OOXML package without opening Microsoft Word.

#### Scenario: DOCX parity validates the renumbered sequence
- **WHEN** the English source DOCX is checked against the reordered English Markdown chapters
- **THEN** the formula-coverage and relevant parity checks identify the same chapter content and numbering without missing formula renderings caused by the prior Chapter 7–10 ordering
