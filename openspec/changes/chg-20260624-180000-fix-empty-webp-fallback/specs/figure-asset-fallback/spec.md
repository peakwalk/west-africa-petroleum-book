## ADDED Requirements

### Requirement: Published figure asset selection skips empty preferred files
The figure inventory publisher MUST ignore zero-byte candidate assets for a figure stem and MUST fall back to the next available non-empty published format according to the existing extension priority.

#### Scenario: Empty WebP falls back to PNG
- **WHEN** `figure-011.webp` exists but has a size of zero bytes
- **AND** `figure-011.png` exists and is non-empty
- **THEN** the published asset candidates for Figure 11 select `figure-011.png` instead of the empty WebP

### Requirement: Figure coverage validation rejects empty published assets
The DOCX figure coverage checker MUST fail when a Markdown-referenced asset or a manifest-selected published asset exists on disk but has a size of zero bytes.

#### Scenario: Empty Markdown target is reported
- **WHEN** a chapter Markdown image reference points to a zero-byte figure asset
- **THEN** the coverage checker reports that reference as an empty asset failure

#### Scenario: Empty manifest-selected asset is reported
- **WHEN** a figure manifest record selects a published asset whose file size is zero bytes
- **THEN** the coverage checker reports that manifest asset as an empty asset failure
