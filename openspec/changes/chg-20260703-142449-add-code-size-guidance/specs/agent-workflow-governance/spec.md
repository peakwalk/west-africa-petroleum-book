## ADDED Requirements

### Requirement: Agents MUST keep handwritten source files reviewable with repo-local size guidance
Agents MUST treat handwritten source-file size as a repository workflow rule. New handwritten source files SHOULD normally stay under 600 lines. Landing-page stylesheets, site templates, and page-generation scripts SHOULD normally stay under 500 lines by extracting coherent partials, helpers, content modules, or smaller generators. Agents MUST NOT introduce a new handwritten source file over 800 lines without documenting a clear reason in the change summary. When editing an existing handwritten source file that already exceeds the applicable threshold, agents MUST avoid increasing its line count, and for non-trivial edits they MUST extract at least one coherent unit unless doing so would create churn unrelated to the task.

#### Scenario: New repo-local source file stays within the normal general threshold
- **WHEN** an agent adds a new handwritten source file in this repository
- **THEN** the file normally stays under 600 lines unless the task clearly needs more

#### Scenario: Landing-page style or generator work uses the stricter repo-specific threshold
- **WHEN** an agent adds or substantially expands a landing-page stylesheet, site template, or page-generation script
- **THEN** the file normally stays under 500 lines by extracting a focused partial, helper, content module, or smaller generator unit

#### Scenario: Existing oversized file is not grown casually
- **WHEN** an agent edits an existing handwritten source file that is already above the applicable threshold
- **THEN** the agent avoids increasing its line count
- **AND** for a non-trivial edit extracts at least one coherent helper, partial, or module unless that extraction would introduce unrelated churn

#### Scenario: Generated and mechanically derived artifacts remain exempt
- **WHEN** a file is generated output, a lockfile, snapshot, fixture dataset, vendored reference, or migration-style artifact
- **THEN** the repo's file-size guidance does not apply to that file
