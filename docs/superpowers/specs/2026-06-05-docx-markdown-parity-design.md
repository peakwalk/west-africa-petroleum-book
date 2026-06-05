# DOCX Markdown Parity Design

## Goal

Keep Markdown as the authoritative publishing source while enforcing that
its chapter structure and visible body content stay aligned with the
reference DOCX manuscript.

## Problem Statement

The current site pipeline publishes `src/chapters/*.md` directly through
mdBook, but those Markdown files have already drifted from the DOCX in
structural ways. A visible example is Chapter 1, where the DOCX renders
`1.1- The Upstream segment` while the published Markdown contains
`1.  ***The Upstream segment***`, which mdBook renders as an ordered-list
item instead of a real section heading.

This is not a browser rendering issue. It is a source-parity issue:

- DOCX and Markdown are not kept in sync.
- Existing conversion output cannot be trusted as ground truth for heading
  structure, because Word automatic numbering can be degraded during
  conversion.
- The current build and test flow has no parity gate, so structural drift
  can be published silently.

## Source of Truth

- `src/chapters/*.md` remains the authoritative source for publication and
  editing.
- `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx`
  is the reference document used for parity validation.
- The DOCX is not used to overwrite Markdown during normal builds.
- Site generation continues to consume Markdown directly.

This means the system must answer one question reliably: does the current
Markdown still represent the same chapter outline and visible content as the
reference DOCX?

## Non-Goals

- Replacing mdBook with a DOCX-driven publishing pipeline.
- Re-generating all Markdown from DOCX on every build.
- Allowing webpage-only patch layers to alter semantic content.
- Solving all DOCX-to-Markdown fidelity problems in one pass.

## Architecture Overview

Add a standalone parity-validation step that compares two normalized semantic
models:

1. A DOCX-derived model extracted directly from Word XML.
2. A Markdown-derived model extracted from the authored `src/chapters`
   files.

The validator runs before site publishing and fails CI when structure or
content drifts beyond explicitly allowed presentation-only differences.

The build path stays unchanged:

- Author edits Markdown.
- mdBook builds from Markdown.
- Parity validation blocks publication when Markdown no longer matches DOCX.

## High-Level Approach Options

### Option 1: Validation Gate Only

Compare DOCX and Markdown in CI, report differences, and require humans to
repair Markdown manually.

Pros:

- Preserves Markdown authority cleanly.
- Avoids pushing converter mistakes back into the repository.
- Keeps the implementation narrowly focused on detection and diagnosis.

Cons:

- Humans still perform the final correction.

### Option 2: Validation Plus Suggested Fixes

Detect drift and emit candidate Markdown patches for review.

Pros:

- Faster repair loop once the validator is mature.

Cons:

- Higher complexity.
- Greater risk of producing incorrect semantic edits, especially around
  heading numbering and nested list structure.

### Option 3: Intermediate Baseline Manifest

Extract DOCX into a committed JSON baseline and validate Markdown against
that baseline instead of the DOCX directly.

Pros:

- Faster CI after the baseline exists.

Cons:

- Introduces another truth layer that can itself go stale.
- Moves the real parity problem from DOCX vs Markdown to DOCX vs baseline vs
  Markdown.

## Recommended Approach

Adopt Option 1.

Markdown remains authoritative, and the DOCX is treated as a reference
constraint checked by a dedicated parity gate. This minimizes system
complexity while preventing silent publication drift.

## Validation Boundaries

### What Must Match

Two dimensions must match between DOCX and Markdown:

1. Outline structure
2. Visible body content

### Outline Structure Requirements

Outline parity means all of the following are equal:

- Chapter and section order
- Hierarchical level
- Number label
- Section title text

For example:

- DOCX: `1.1- The Upstream segment`
- Markdown: `1. The Upstream segment`

This is an outline mismatch even though the title text is similar, because
the numbering label and semantic level differ.

### Visible Body Content Requirements

Body parity compares normalized visible semantics rather than raw source
syntax. The validator must compare:

- Section headings
- Paragraph text
- Ordered-list item text
- Unordered-list item text
- Figure captions
- Table captions when represented as visible text

The validator does not compare raw Markdown formatting or HTML wrappers.

## Allowed Differences

The validator may ignore only presentation-only differences, including:

- Line wrapping
- Extra whitespace
- Markdown emphasis markers
- Equivalent HTML/Markdown formatting wrappers
- Internal anchor markup
- Image format substitutions such as `.png` vs `.webp`
- Explicitly marked webpage-only helper blocks

These ignored regions must not affect semantic reading content.

## Disallowed Differences

The validator must fail on any of the following:

- Section numbering changes
- Section level changes
- Section title text changes
- Added or removed paragraphs
- Added or removed list items
- Reordered content blocks
- Figure caption text changes
- Semantic content edits hidden inside webpage-only patch zones

## Webpage-Only Patch Layer Policy

Small webpage-only patch layers are allowed, but only for presentation.

Allowed examples:

- Anchor wrappers
- Layout helper containers
- Responsive-only helper markup
- Reading-time ignore containers
- Image resource swaps

Disallowed examples:

- Changing heading numbering
- Rewriting titles
- Editing paragraph meaning
- Collapsing a section heading into a list item
- Altering figure caption wording

To make this machine-checkable, webpage-only non-semantic regions must be
marked explicitly with a parity-ignore mechanism that the Markdown extractor
understands and removes from the semantic model.

## Implementation Shape

The parity checker should be implemented as a standalone Python entrypoint
using the standard library, then exposed through npm scripts.

This avoids adding runtime dependencies and avoids assuming `pandoc` exists
in CI.

### Proposed Files

- `scripts/check_docx_parity.py`
  CLI entrypoint. Parses arguments, runs extraction and comparison, prints
  reports, and sets the exit code.
- `scripts/docx_parity/__init__.py`
  Package marker.
- `scripts/docx_parity/extract_docx.py`
  Extracts the DOCX semantic model from Word XML.
- `scripts/docx_parity/extract_markdown.py`
  Extracts the Markdown semantic model from `src/chapters` and `src/SUMMARY.md`.
- `scripts/docx_parity/normalize.py`
  Shared normalization rules used by both extractors.
- `scripts/docx_parity/compare.py`
  Compares the two semantic models and produces structured diffs.
- `scripts/docx_parity/report.py`
  Renders readable diagnostics for terminal and CI output.
- `tests/docx_parity/`
  Python `unittest` coverage for extraction, normalization, and comparison.

## DOCX Extraction Design

DOCX extraction must not trust converter output as the structural truth
source. It must read Word XML directly:

- `word/document.xml`
- `word/numbering.xml`
- `word/styles.xml` when style fallback is needed

### Why Direct XML Extraction Is Required

The current issue exists precisely because converter output degraded Word
automatic numbering into a plain ordered list. If the validator only compares
Markdown against converted DOCX text, it can inherit the same mistake and
miss real outline drift.

Direct XML extraction avoids that failure mode by reconstructing the numbering
semantics Word actually displays.

### DOCX Numbering Recovery

The extractor must reconstruct displayed numbering using:

- `numId -> abstractNumId`
- `abstractNumId + ilvl -> lvlText`
- `numFmt`
- `start`

As the document is traversed in order, the extractor maintains counters per
numbering hierarchy and expands level text templates such as:

- `%1.%2-`
- `%1.%2.%3-`

This allows the DOCX semantic model to store the true visible label and title
pair, for example:

- `number`: `1.1-`
- `title`: `The Upstream segment`

### DOCX Output Model

The extractor should emit two coordinated structures:

- `outline`
  - chapter/section order
  - depth level
  - numbering label
  - title text
- `body`
  - normalized visible paragraph and list content in document order
  - figure captions
  - heading text instances as visible content

## Markdown Extraction Design

Markdown extraction should stay conservative and dependency-light. It does not
need a full Markdown AST for the first version.

### Inputs

- `src/SUMMARY.md`
- `src/chapters/*.md`

### Markdown Structures to Recognize

- ATX headings: `#`, `##`, `###`, etc.
- Ordered lists
- Unordered lists
- Plain paragraphs
- Figure caption lines such as `Figure 1: ...`
- Explicit parity-ignore regions

### Markdown Output Model

Like the DOCX extractor, it emits:

- `outline`
  - order
  - level
  - numbering label parsed from visible heading/list text
  - title text
- `body`
  - normalized visible text blocks in document order

## Chapter Mapping Strategy

Markdown chapters are mapped from `src/SUMMARY.md`.

The validator should split DOCX content into chapter segments using the DOCX
outline, then map those segments against the Markdown files listed in
`SUMMARY.md`.

Word's built-in table of contents may be used only as a secondary
cross-check. It must not be treated as the primary source of semantic truth,
because TOC correctness does not guarantee body correctness.

## Difference Types

The comparison layer should produce explicit difference categories instead of
a generic text mismatch.

Minimum categories:

- `outline.number_mismatch`
- `outline.level_mismatch`
- `outline.title_text_mismatch`
- `outline.order_mismatch`
- `body.paragraph_mismatch`
- `body.list_item_mismatch`
- `body.figure_caption_mismatch`
- `body.block_missing`
- `body.block_extra`

For the current Chapter 1 issue, the desired failure classification is:

- `outline.number_mismatch`

with diagnostics similar to:

- DOCX: `1.1- The Upstream segment`
- Markdown: `1. The Upstream segment`

## CLI Contract

Expose the validator through npm, but keep the implementation in Python.

### Commands

- `npm run check:docx-parity`
  Validate the full book against the reference DOCX.

Optional CLI flags:

- `--chapter <path>`
  Validate a single Markdown chapter file.
- `--docx <path>`
  Override the reference DOCX path.
- `--json`
  Emit machine-readable diff output.

## CI Integration

The parity gate should run before site publication.

### Package Scripts

Add:

- `check:docx-parity`

Update:

- `test:site` to run parity validation before the site assertions

### GitHub Pages Workflow

In `.github/workflows/pages.yml`, run parity validation before `npm run build:site`.

If parity fails:

- The workflow fails.
- The site is not published.

## Reporting Format

Failure output must be concise and directly repairable.

Recommended format:

```text
src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md
  type: outline.number_mismatch
  docx:      1.1- The Upstream segment
  markdown:  1. The Upstream segment
  hint: Promote this item to a real section heading and preserve the DOCX numbering label.
```

Required report fields:

- chapter path
- difference type
- DOCX normalized snippet
- Markdown normalized snippet
- short repair hint

## Testing Strategy

Use Python standard-library `unittest` so tests run in CI without new
dependencies.

### Unit Tests

At minimum:

- DOCX numbering reconstruction
  - Recover `1.1-`
  - Recover `1.1.1-`
- Markdown extraction
  - Detect headings, lists, figure captions, and ignored regions
- Normalization
  - Ignore whitespace and formatting noise
  - Preserve numbering differences
- Comparison
  - Classify the Chapter 1 example as `outline.number_mismatch`

### Integration Tests

Add a real-book integration test that validates the current manuscript
against a focused chapter subset, initially Chapter 1, so the validator is
proven against the live source shape.

The first expected outcome before content repair is failure on the known
outline mismatch. Once content is corrected, the test expectation flips to
success.

## Rollout Plan

### Phase 1

- Build the parity validator and its tests.
- Wire it into npm scripts and CI.
- Do not yet modify chapter content automatically.

### Phase 2

- Repair existing Markdown drift until the validator passes.
- Start with Chapter 1 and other chapters already known to have degraded
  numbered headings.

### Phase 3

- Optionally add JSON output improvements or authoring ergonomics, but keep
  the validator read-only with respect to Markdown semantics.

## Success Criteria

The design is successful when all of the following are true:

- Markdown remains the publishing authority.
- DOCX remains the parity reference.
- Known numbering drift such as `1.1-` becoming `1.` is detected reliably.
- Webpage-only presentation patches do not create false failures.
- CI blocks publication when semantic drift exists.
- Humans can repair failures from the parity report without reverse
  engineering the validator.

## Risks and Mitigations

### Risk: Word numbering complexity is underestimated

Mitigation:

- Restrict the first version to the numbering patterns already present in the
  manuscript.
- Add fixtures for every discovered numbering pattern before expanding
  support.

### Risk: Markdown parsing misses edge cases

Mitigation:

- Keep extraction rules conservative.
- Treat ambiguous constructs as mismatches rather than silently accepting
  them.

### Risk: Presentation-only helpers pollute semantic comparison

Mitigation:

- Require explicit parity-ignore markers.
- Document their allowed usage clearly.

## Final Recommendation

Implement a read-only DOCX parity validator that compares a directly
extracted DOCX semantic model against the authored Markdown semantic model,
then enforce it in CI before publication.

This keeps authority where the team wants it, catches the exact class of
structural drift already present in the book, and avoids introducing another
generated source of truth.
