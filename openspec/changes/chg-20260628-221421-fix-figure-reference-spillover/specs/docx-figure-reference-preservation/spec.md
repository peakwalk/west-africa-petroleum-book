## ADDED Requirements

### Requirement: Figure reference prose before a standalone caption MUST remain paragraph body text
The DOCX semantic extractor MUST preserve a prose paragraph that references a figure number when that paragraph is followed by a standalone figure caption paragraph for the same figure.

#### Scenario: Chapter-opening figure lead-in is preserved before the caption
- **WHEN** a chapter body paragraph says a figure illustrates some concept and includes `Figure 5:` inline as part of ordinary prose
- **AND** the next non-empty paragraph is a standalone `Figure 5 ...` caption
- **THEN** the extractor keeps the prose sentence as a paragraph body block
- **AND** the extractor emits the standalone `Figure 5 ...` paragraph as a caption block

### Requirement: Synthetic caption spillover MUST require embedded-caption evidence
The DOCX semantic extractor MUST NOT synthesize a caption block from a mixed prose paragraph unless the paragraph contains embedded-caption spillover evidence such as glued text, duplication, or other conditions already recognized as spillover.

#### Scenario: Ordinary prose with a figure reference is not truncated into a caption
- **WHEN** a paragraph contains ordinary prose before the `Figure N:` marker
- **AND** the paragraph does not satisfy the extractor's spillover-caption test
- **THEN** the extractor does not split that paragraph into a synthetic caption fragment
