## Context

The English reference PDF and the raw Chapter 5 DOCX content both contain a prose lead-in sentence before Figure 5, followed by a standalone figure caption paragraph. The current DOCX semantic extractor treats any pre-outline paragraph containing `Figure N:` as caption spillover, even when the paragraph is ordinary prose and a separate caption follows immediately after. That misclassification propagates into replacement Markdown content, site rendering, and parity-driven rebuild workflows.

## Goals / Non-Goals

**Goals:**
- Preserve figure-reference prose paragraphs as normal body text when they are followed by a standalone figure caption paragraph.
- Keep true spillover caption normalization working for concatenated or duplicated pre-heading caption artifacts.
- Add a regression test that covers both `extract_docx_book` and `extract_docx_chapter_by_anchors`.

**Non-Goals:**
- Rebuild the full English edition in this change.
- Redesign the full DOCX figure extraction pipeline.
- Change how standalone `Figure N ...` caption paragraphs are recognized.

## Decisions

### Decision: Require actual spillover evidence before synthesizing a caption from mixed prose
The narrowest fix is to stop treating every pre-outline paragraph that happens to contain a caption substring as a synthetic caption. The extractor already has `_is_spillover_caption(...)`, which distinguishes real glued spillover from normal prose by checking whether the caption marker is embedded in or duplicated within the same paragraph. Reusing that signal avoids broad heuristic churn.

Alternative considered:
- Special-case sentences that start with `The` or contain commas. Rejected because it hard-codes English prose patterns and would be brittle across future content.

### Decision: Cover both full-book and anchor-based extraction in one regression test
The buggy heuristic is duplicated in `extract_docx_book` and `extract_docx_chapter_by_anchors`. The regression needs to exercise both paths so a future one-sided edit cannot silently reintroduce the mismatch in parity-only workflows.

Alternative considered:
- Test only `extract_docx_book`. Rejected because the user-visible parity workflows also rely on anchor-based extraction.

## Risks / Trade-offs

- [A true pre-outline spillover paragraph without glued caption evidence] → The extractor may stop normalizing that paragraph as a caption. Mitigation: keep standalone caption handling unchanged and preserve existing explicit spillover tests.
- [Duplicated logic drift between the two extraction functions] → One path could regress independently later. Mitigation: one regression test will assert both paths produce the same preserved paragraph-plus-caption output.

## Migration Plan

1. Add a failing DOCX extraction regression test for a chapter-opening figure reference sentence followed by a standalone caption.
2. Tighten the spillover-caption condition in both extraction paths.
3. Run targeted extraction tests plus the narrow Chapter 5 parity check.
4. If rollback is needed, restore the prior spillover condition and remove the regression test.

## Open Questions

- None.
