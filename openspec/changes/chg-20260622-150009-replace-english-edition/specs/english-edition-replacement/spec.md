## ADDED Requirements

### Requirement: English replacement MUST preserve French edition immutability
The repository MUST support replacing the English manuscript, navigation, content, and figure assets without modifying French summary structure, French chapter files, French figure assets, or French manuscript aliases.

#### Scenario: English alias cutover leaves French manuscript aliases untouched
- **WHEN** the English replacement is finalized
- **THEN** only `resources/editions/en/reference.docx` and `resources/editions/en/reference.pdf` change targets, while `resources/editions/fr/reference.docx` and `resources/editions/fr/reference.pdf` remain unchanged

#### Scenario: English content rebuild leaves French navigation unchanged
- **WHEN** English `SUMMARY.md` and English chapter files are rewritten for the replacement release
- **THEN** `editions/fr/content/SUMMARY.md` and `editions/fr/content/chapters/*` remain unchanged in the same change set

### Requirement: English navigation MUST be regenerated from the replacement manuscript topology
The English edition MUST derive its `SUMMARY.md`, chapter inventory, and reader sidebar from the replacement English manuscript's actual front matter, top-level sections, and back matter. The retired six-chapter English topology MUST NOT be retained as a compatibility shell when it no longer matches the manuscript.

#### Scenario: English summary matches the replacement manuscript structure
- **WHEN** the English summary is generated for the replacement release
- **THEN** it enumerates the replacement manuscript's front matter and top-level section order rather than the retired six-chapter outline

#### Scenario: English parity no longer extracts zero content blocks
- **WHEN** `python3 scripts/check_docx_parity.py --edition en` runs after English cutover
- **THEN** the English chapter set is extracted from the replacement manuscript using its new anchors and does not report zero extracted outline or body blocks for every chapter

### Requirement: English content and figures MUST converge to the replacement manuscripts
The English edition MUST rebuild chapter Markdown, figure manifests, and published figure assets from the replacement English DOCX/PDF. Legacy English figures or chapter text that exist only in the retired manuscript MUST be removed from the published English set before release.

#### Scenario: English figure manifest is built from the replacement manuscript
- **WHEN** `python3 scripts/build_docx_figure_manifest.py --edition en` runs for the replacement release
- **THEN** the resulting manifest reflects the replacement English manuscript's figure inventory and published asset paths

#### Scenario: Replacement English raster figures keep numbered PNG exports and canonical WebP references
- **WHEN** replacement English raster figures are rebuilt from the DOCX/PDF pair
- **THEN** each rendered figure keeps a same-numbered `figure-NNN.png` export, generates a matching `figure-NNN.webp` asset for web delivery, and the manifest plus chapter markdown reference the `webp` asset when both files exist

#### Scenario: Retired English-only material does not survive cutover
- **WHEN** a figure or chapter section exists only in the retired English manuscript
- **THEN** that figure or section is absent from the published English markdown and asset tree after cutover

### Requirement: English cutover MUST use staged validation and rollback
The English replacement MUST be validated against the replacement manuscripts before the canonical English aliases are switched. The final cutover MUST be reversible by restoring the previous English alias targets and English content tree from Git without modifying French files.

#### Scenario: Pre-cutover validation can run without alias switch
- **WHEN** the replacement English content is still under construction
- **THEN** parity and figure-validation commands can target the replacement English DOCX/PDF via explicit command arguments while the canonical English aliases still point to the retired manuscript

#### Scenario: English rollback is English-only
- **WHEN** the replacement English release needs to be rolled back
- **THEN** rollback restores the previous English alias targets and English content/figure files without touching French summary, French chapters, or French figure assets

### Requirement: Reader entry and cross-edition links MUST follow the active edition topology
After the English replacement, reader entry routes and language-switch links MUST resolve against the active edition's real page topology instead of assuming English and French share the same slugs. When no close peer page exists in the other edition, the link MUST fall back to the peer reader home rather than pointing at a non-existent chapter path.

#### Scenario: English and French reader homes keep different first readable pages
- **WHEN** a reader opens `/book` for English or `/fr/book` for French
- **THEN** English resolves to `chapters/disclaimer.html` while French resolves to `chapters/foreword.html`

#### Scenario: Unique English pages do not generate dead French links
- **WHEN** a reader uses the language switch from an English-only page such as `disclaimer.html`, `preface.html`, or a replacement-only chapter without a close French peer
- **THEN** the switch targets `/fr/book/?lang=fr` instead of a non-existent `/fr/book/chapters/<same-slug>.html`

#### Scenario: Topic-equivalent pages keep direct cross-edition links
- **WHEN** a reader uses the language switch from a page whose topic has a clear peer in the other edition
- **THEN** the switch links directly to that mapped peer page, such as English `chapter-05-hydrocarbon-value-chain.html` to French `chapter-01-value-chain-of-the-hydrocarbon-sector.html`
