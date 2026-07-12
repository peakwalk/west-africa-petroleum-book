## Context

UA-16 is an English-edition structure change. The intended chapter is the existing `chapter-10-petroleum-data-management-in-west-africa.md`; its ticket title incorrectly calls it Petroleum Development Management. The current English sequence places it after Chapter 9. The approved sequence is Chapter 5, Chapter 6, data management as Chapter 7, then the former Chapters 7, 8, and 9 as Chapters 8, 9, and 10; Chapters 11 and 12 retain their numbers.

mdBook derives the reader order, sidebar, and previous/next links from `SUMMARY.md`. The repository also contains hand-authored table, figure, table, and equation indexes plus a chapter-library generator that categorizes part headings. Public chapter filenames are published URLs and are separate from their display numbers.

## Goals / Non-Goals

**Goals:**

- Give English readers the approved learning sequence and matching Part II and Part III headings.
- Keep every visible chapter number, numbered heading, manual index, and prose cross-reference internally consistent.
- Align canonical chapter URLs with display numbers, preserve former routes through redirects, and regenerate all derived site output.
- Limit the change to the English edition, source-controlled text/configuration, and its separately managed local source reference DOCX.

**Non-Goals:**

- Do not rewrite chapter prose, regenerate figures, alter French content, or hand-edit `public/`.
- Do not retain the former mismatched chapter URLs as canonical pages.

## Decisions

### Use `SUMMARY.md` as the structural source of truth

The English summary will place the data-management source file after Chapter 6 and start Part III at the former Chapter 7. This lets mdBook derive sidebar and previous/next navigation instead of maintaining a second navigation order.

Alternative considered: rearranging generated HTML only. Rejected because the next build would overwrite it and the source summary would remain incorrect.

### Align canonical file paths with display numbering and preserve legacy entry points

The four affected chapter source files and canonical public routes use their revised Chapter 7 through Chapter 10 numbers. A build-time redirect generator creates non-canonical pages at the former routes, preserves query strings and fragments, and points visitors to the matching canonical route. English-to-French navigation and SEO maps use canonical route keys.

Alternative considered: keep mismatched filenames indefinitely. Rejected because route names must describe their displayed chapters. A redirect is required because renaming without one would break inbound links.

### Apply an explicit number map to all numbered content

The implementation map is: `10 → 7` for data management, `7 → 8` for petroleum fiscal regimes, `8 → 9` for West African fiscal regimes, and `9 → 10` for socio-political determinants. It applies to chapter titles, section labels, equation identifiers, manual indexes, and intentional prose references; it does not alter figure/table ordinal identifiers.

Alternative considered: broad project-wide text replacement. Rejected because historical statements, URLs, and unrelated numerical content could be changed incorrectly.

### Keep Chapter 5 in Part II and scope the change to English

Chapter 5 remains in Part II: it is currently part of that section, and moving only Chapters 6–7 into Part II would orphan it. The French edition has a distinct six-chapter structure and receives no speculative renumbering.

Alternative considered: apply the ticket wording literally and omit Chapter 5. Rejected because every chapter must remain in exactly one part.

### Synchronize the English reference DOCX directly at the OOXML layer

The source `resources/editions/en/reference.docx` has the former Chapter 7–10 order, which makes positional DOCX checks compare the wrong chapters after the Markdown migration. Move the complete DOCX chapter blocks to the approved order and apply the same explicit number map to their chapter and section labels. Preserve package parts and formatting; make the change through the DOCX ZIP/XML package only, without opening Microsoft Word.

Alternative considered: weaken or bypass formula-coverage validation. Rejected because it would hide real divergence between the English source document and reader edition.

## Risks / Trade-offs

- [Numbered in-page anchors change] → Update internal manual-index links and validate generated HTML. Existing external deep links to old numeric anchors remain a documented breaking change.
- [Canonical chapter URLs change] → Generate and test static compatibility redirects that preserve query strings and fragments; exclude redirect pages from the sitemap.
- [Hand-authored indexes drift] → Regenerate their chapter blocks from the changed source headings and inspect each index.
- [Part-title recognition in the chapter-library generator becomes stale] → Add the new English Part II and III labels to its categorization map and verify the generated landing page.
- [Direct OOXML editing could corrupt the DOCX or leave stale field caches] → write through a temporary package, validate ZIP/XML structure and DOCX parity/formula coverage, then render it with the packaged renderer and inspect representative pages. Set fields to update on the next compatible office open where necessary, without using Word in this workflow.
- [The reference DOCX is a Git-ignored symlink] → do not force-add it or claim it will be pushed with the source change. Its external target must be distributed or reconciled through an explicitly approved artifact workflow before a Git-only release can be considered complete.
- [Unrelated worktree changes] → Leave figure assets and any unrelated files untouched; review the final diff by path before completion.

## Migration Plan

1. Update the English source order and number map, then update source indexes and generator recognition.
2. Synchronize the English reference DOCX directly, then validate its chapter alignment and formula coverage.
3. Build the site into the generated output directory and validate navigation, headings, anchors, routes, and generated chapter metadata.
4. If validation fails, restore the pre-edit reference DOCX from the temporary backup and revert only this change's source edits before rebuilding; the legacy redirect map can be removed together with the renamed canonical routes.

## Open Questions

- None. The user confirmed that the existing data-management chapter is the target referenced by UA-16.
