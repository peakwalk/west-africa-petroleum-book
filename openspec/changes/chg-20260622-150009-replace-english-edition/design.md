## Context

The repo already separates English and French by edition root, but the current English edition still reflects the retired English manuscript's information architecture. The new English DOCX/PDF pair added under `resources/` is materially different from the current English release in both scope and layout.

Observed evidence from the current workspace:

- The retired English DOCX is about 11.3 MB with about 1,074 non-empty paragraphs, while the replacement English DOCX is about 83.7 MB with about 9,135 non-empty paragraphs.
- The current English `SUMMARY.md` publishes six body chapters plus front/back matter, while the replacement manuscript exposes a new top-level structure spanning at least 12 heading-1 sections from `General Introduction` through `Vision for West Africa 2050`, plus disclaimer/preface/list material.
- Running `python3 scripts/check_docx_parity.py --edition en --docx 'resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx'` currently yields `outline.entry_count_mismatch`, `body.block_count_mismatch`, and `body.sequence_mismatch` for every English chapter, with extracted DOCX outline/body counts of `0`, which proves the old English anchor model cannot be reused as-is.

This is therefore not a chapter refresh. It is an English-edition rebuild problem with two fixed constraints:

1. the English source of truth must move to the new manuscript;
2. the French edition must keep its current navigation, content, figure assets, and manuscript aliases unchanged.

## Goals / Non-Goals

**Goals:**
- Replace the English edition with the new English manuscript as the sole canonical English source.
- Rebuild English navigation, chapter topology, and supporting content so the published English book matches the replacement manuscript instead of the retired six-chapter shell.
- Keep the French edition unchanged in source ownership, navigation, content, figure assets, and manuscript aliases.
- Stage the English cutover so validation can run before the canonical English aliases switch.
- Preserve an English-only rollback path that restores the prior release without any French edits.

**Non-Goals:**
- Updating the French edition to mirror the new English manuscript.
- Preserving the retired English six-chapter navigation or forcing the new manuscript into the old slug tree.
- Hand-editing `public/` output or bypassing the established edition build pipeline.
- Solving every future multilingual divergence problem beyond what is required for this English replacement.

## Decisions

### 1. Treat the new English manuscript as a full replacement, not an incremental overwrite

First principle: the canonical English book is the manuscript, not the current Markdown tree. Because the new manuscript differs in scale, chapter system, and navigation semantics, the migration must start from the replacement manuscript and rebuild the English edition around it.

Alternative considered:
- Overwrite the current English chapters in place while preserving the old structure. Rejected because it would keep a misleading English sidebar and guarantee chronic parity drift between manuscript and published book.

### 2. Defer the English alias switch until the rebuilt content validates

The repo already has a useful indirection layer in `resources/editions/en/reference.docx` and `reference.pdf`. During the rebuild, those English aliases should keep pointing at the retired manuscript. Validation should target the replacement English files via explicit `--docx` and `--pdf` arguments until the rebuilt English content, figure assets, and manifest are ready.

This separates manuscript cutover from content reconstruction:

- rebuild work can proceed without breaking the current English release baseline;
- the final alias change becomes one explicit release step;
- rollback remains a small English-only alias reversion plus Git restore of English content/assets.

Alternative considered:
- Repoint the English aliases first and repair the content tree afterward. Rejected because it would immediately make English parity checks fail against a knowingly stale content tree.

### 3. Rebuild English navigation from the replacement manuscript and allow English-only topology divergence

The English left navigation must be regenerated from the replacement manuscript's actual structure. That means:

- rewriting `editions/en/content/SUMMARY.md`;
- redefining the English chapter file inventory under `editions/en/content/chapters/`;
- reclassifying front matter and back matter around the replacement manuscript's disclaimer, preface, numbered body chapters, glossary, and bibliographical references, while treating figure/table indexes as synthetic web utilities rather than manuscript-native chapters.

The French edition must keep its current `SUMMARY.md` and chapter set. Symmetry between editions is no longer the right invariant for this change; edition isolation is.

Alternative considered:
- Keep the English and French navigation trees mirrored. Rejected because the user explicitly requires French to remain unchanged and the new English book is no longer structurally parallel to the French one.

### 4. Split the work into four MECE migration tracks

To avoid cross-coupled execution, the change should be decomposed into four non-overlapping workstreams:

1. **Structure and anchors**: chapter inventory, `SUMMARY.md`, parser rules, front/back matter boundaries.
2. **Narrative content**: English chapter markdown, headings, lists, disclaimers, and supporting reader-facing copy.
3. **Figures and tables**: figure inventory, manifest, rendered assets, references, and retirements.
4. **Release safety**: alias cutover, regression checks, rollback procedure, and change notes.

This is the MECE boundary that keeps content decisions from being hidden inside asset or validation work.

Alternative considered:
- Bulk-convert everything in one pass and fix failures afterward. Rejected because it would mix source-structure errors, figure errors, and release-cutover errors into one failure domain.

### 5. Harden the English parity pipeline before rewriting content at scale

The current English parity failure mode shows that `scripts/docx_parity/extract_docx.py` and related logic still assume the retired manuscript's anchor model. The extraction/parity layer must first learn the replacement manuscript's chapter boundaries and supporting material so that the rebuilt English content can be validated incrementally.

In practice, that means:

- adding or refining replacement-English chapter boundary rules;
- allowing the checker to validate the new English structure before alias cutover;
- protecting French extraction behavior with regression checks after parser changes.

Alternative considered:
- Skip parity and rely on manual review plus `mdbook build`. Rejected because the manuscript/content drift is exactly what parity is supposed to control, and the change scope is too large for manual review alone.

### 6. Freeze French as an explicit regression boundary

French is not merely "out of scope"; it is a protected boundary for this change. The implementation should assume:

- no edits under `editions/fr/**`;
- no edits to `resources/editions/fr/reference.*`;
- any shared parser or build-script change must be followed by the narrowest French regression checks.

Alternative considered:
- Opportunistically propagate English structural changes into the French tree for future consistency. Rejected because it directly violates the user's constraint and expands the risk surface without solving the current problem.

### 7. Publish replacement-English raster figures as PNG plus WebP, with PDF-first rendering and single-image DOCX fallback

For the replacement English manuscript, the stable figure identifier is the figure number, not the source container format. Raster figures should therefore publish as a numbered PNG sidecar plus a same-numbered WebP asset:

- `figure-NNN.png` remains the stable export and rollback-friendly source artifact;
- `figure-NNN.webp` is the canonical web-facing asset referenced by chapter markdown and the figure manifest when both files exist.

Rendering should stay PDF-first for fidelity. However, the replacement manuscript includes bitmap figures that are flattened inside the DOCX, and at least one of them can defeat the PDF white-region detector. When a requested English replacement figure fails PDF cropping but still has exactly one embedded bitmap source in the DOCX, the pipeline should fall back to DOCX bitmap extraction for that figure number instead of failing the whole batch.

Alternative considered:
- Keep PNG-only publication for replacement-English raster figures. Rejected because it degrades web delivery and leaves chapter references inconsistent with the repo's preferred WebP-first publishing pattern.
- Fail the full PDF batch when a single replacement-English bitmap cannot be auto-cropped. Rejected because it blocks the release on one detector edge case even when a safe single-image DOCX fallback exists.

## Risks / Trade-offs

- [The replacement manuscript's TOC styling is inconsistent, including a visible numbering gap around sections 8-10 in raw extraction] -> Normalize structure from heading analysis plus manual manuscript review instead of trusting raw TOC text alone.
- [Some English figure numbers may be reused while the underlying layout changes] -> Treat figure-number reuse as content change, rebuild the English manifest from the replacement manuscript, and re-render changed assets instead of assuming asset continuity.
- [Old English chapter URLs may stop matching the new navigation tree] -> Decide and document the post-cutover deep-link policy before rewriting `SUMMARY.md`; if compatibility is required, add redirect or tombstone handling as a separate explicit task.
- [Shared parser changes could accidentally regress the French edition] -> Run the narrowest French parity and figure regression checks after parser changes, even though French files themselves are frozen.
- [Deferring the alias switch means the repo temporarily carries old aliases plus new candidate content in the same branch] -> Accept the temporary dual-state during implementation because it sharply reduces release risk and makes rollback trivial.

## Migration Plan

1. Capture the replacement English manuscript's top-level structure, front matter, back matter, and figure inventory as the baseline evidence for the change.
2. Update the English DOCX extraction/parity workflow so it can parse the replacement manuscript via explicit `--docx`/`--pdf` arguments while the English aliases still point to the retired manuscript.
3. Rewrite English `SUMMARY.md`, chapter files, and any English reader-facing metadata to match the replacement manuscript's information architecture.
4. Rebuild the English figure manifest and published figure assets from the replacement English DOCX/PDF, then update chapter references and remove retired assets.
5. Repoint `resources/editions/en/reference.*` to the replacement English files and run the narrowest relevant English release checks plus French regression checks.

Rollback strategy:

- restore `resources/editions/en/reference.docx` and `reference.pdf` to the retired manuscript targets;
- restore `editions/en/content/**` and English figure assets from Git;
- do not touch `editions/fr/**` or `resources/editions/fr/**`.

## Open Questions

- Do legacy English chapter deep links need compatibility handling after the new English navigation tree is finalized, or is it acceptable for the English chapter URL set to change with the replacement manuscript?
- Is the apparent missing top-level section between the replacement manuscript's raw `8.*` and `10.*` TOC entries a real editorial merge or a DOCX style defect that must be normalized during extraction?
