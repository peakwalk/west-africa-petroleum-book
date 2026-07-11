## Why

UA-19 identifies technical inaccuracies in the English online book's Figures 9, 41, and 69. The Jira attachments retain development-era filenames that are one number lower than the displayed online figure numbers, so treating those attachment names as published asset names could overwrite the unrelated Figures 8, 40, and 68.

This change corrects the three technical figures while preserving their captions, references, visual style, and the integrity of the English and French editions.

## What Changes

- Replace the English published artwork for online Figures 9, 41, and 69 using the corresponding UA-19 attachment artwork as the source:
  - Jira `figure-008.png` -> online Figure 9 -> `figure-009.png` and `figure-009.webp`
  - Jira `figure-040.png` -> online Figure 41 -> `figure-041.png` and `figure-041.webp`
  - Jira `figure-068.png` -> online Figure 69 -> `figure-069.png` and `figure-069.webp`
- Apply UA-19's terminology, workflow-direction, and PSC revenue-flow corrections to the three figures.
- Preserve the existing English chapter references, captions, online figure numbers, and Upstream Atlas visual style.
- Regenerate English figure metadata and add a focused regression check for the attachment-to-published-asset mapping.
- Capture reproducible baseline screenshots before implementation and matching updated screenshots after implementation for paired human review.

## Capabilities

### New Capabilities

- `technical-figure-corrections`: Safely publish reviewed technical figure corrections when Jira source artwork filenames differ from online figure asset filenames.

### Modified Capabilities

- None.

## Impact

- Affected assets: `editions/en/content/images/figure-009.{png,webp}`, `figure-041.{png,webp}`, and `figure-069.{png,webp}`.
- Affected metadata and verification: the English figure manifest and focused figure-reference tests.
- Review evidence: paired screenshots under `output/playwright/ua-19-technical-figure-corrections/`.
- No change to `public/`, English chapter Markdown, French assets, or Figures 8, 40, and 68 is in scope.
