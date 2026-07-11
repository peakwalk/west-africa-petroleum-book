## Context

The English edition keeps source PNGs and published WebPs under `editions/en/content/images/`. The online Figure 9, Figure 41, and Figure 69 chapter references already resolve to `figure-009.webp`, `figure-041.webp`, and `figure-069.webp`. UA-19 supplies their original artwork using development-era filenames one number lower.

The target figures are bitmap assets, not PDF-backed figures, so this change updates the supplied raster artwork and regenerates the matching WebP output. `public/` remains a generated build artifact.

### Source intake evidence

The supplied UA-19 attachments were staged outside the repository and visually verified before publication:

| Jira source | Target online figure | SHA-256 | Dimensions |
| --- | --- | --- | --- |
| `figure-008.png` | 9 -> `figure-009` | `de34cb042c1f3328a5e727b752cb6f861847636c1b86c0009e1d6eab755788eb` | 1536 x 1024 |
| `figure-040.png` | 41 -> `figure-041` | `216d24d46e3ae41488fbfea767d5f181ccae480bdeddbe4463251f5b53f6882d` | 1131 x 1391 |
| `figure-068.png` | 69 -> `figure-069` | `b539215fc11f36d6afcd2f2e4200c6164fdf02d2069cb7b2ed02b005be4c57af` | 1536 x 1024 |

The staged artwork already contains UA-19's requested corrections. It is therefore published without generative or manual redrawing, preserving the reviewed text, arrows, and layout exactly.

## Goals / Non-Goals

**Goals:**

- Correct the three reviewed English figures using the UA-19 attachments as source artwork.
- Preserve the online-figure-to-published-asset mapping, chapter references, captions, and visual identity.
- Make the source-to-target name translation explicit and testable.
- Verify the asset inventory, generated site, and visual result before delivery.

**Non-Goals:**

- Changing Figures 8, 40, or 68; French-edition assets; chapter prose; captions; or figure numbering.
- Manually editing generated `public/` output.
- Adding fiscal stages not required by UA-19, such as a separate royalty deduction stage.
- Redesigning the wider figure system or replacing the three diagrams with new styles.

## Decisions

### Treat the online figure number as the delivery key

The final asset names use the displayed online figure number: 9 maps to 009, 41 to 041, and 69 to 069. Jira attachment filenames are retained only in temporary intake records and provenance notes.

This prevents a lower-numbered attachment from overwriting the valid, unrelated Figures 8, 40, and 68. Renaming chapter references to the Jira names was rejected because existing Markdown already points to the correct online figure assets.

### Use the Jira attachments as source artwork and generate WebP from the revised PNGs

Each attachment is downloaded to a temporary staging location, inspected for the expected subject, and fingerprinted before editing. The revised PNG is saved under the target online figure number and converted through the repository's lossless WebP helper.

Editing only WebP was rejected because it loses the editable PNG source and makes the next revision harder to trace. Directly editing `public/` was rejected because site builds overwrite it.

### Keep content changes narrow and technically explicit

Figure 9 changes only the two requested labels and preserves product order. Figure 41 uses directional arrows from Integration and Modelling outputs into Evaluation and Recovery Options and has no dangling arrows. Figure 69 represents precisely the five requested stages; Cost Oil / Cost Gas is separated from Profit Oil / Profit Gas, then split into Government and Contractor shares.

The project will not infer an additional generic PSC step. Individual contracts can apply royalties and taxes differently, while UA-19 defines the required simplified teaching flow.

### Combine automated checks with visual acceptance

Automated checks establish that assets, manifests, references, and generated pages are valid. A human visual review establishes correctness of labels, arrows, crop, typography, and diagram semantics, which file-level tests cannot prove.

### Capture paired review evidence at a fixed viewport

Before modifying any target figure, the project captures one baseline screenshot for each affected English figure from the built reader. After implementation, it captures the same three pages using the same browser engine, viewport, route, and naming convention. The artifacts are stored under `output/playwright/ua-19-technical-figure-corrections/baseline/` and `output/playwright/ua-19-technical-figure-corrections/updated/` and delivered together for review.

Using arbitrary local image previews was rejected because it would not prove the published reader presentation. Using a full Playwright evidence lane was rejected because the repository has no desk-check adapter or report-capable browser-test contract for this static visual comparison; the manual visual evidence lane retains reproducible route and viewport data instead.

## Risks / Trade-offs

- [A Jira attachment has the wrong subject or is not the approved source] -> Compare subject, dimensions, and hash during intake; stop and report a mismatch before replacing any asset.
- [A low-numbered attachment overwrites an unrelated figure] -> Use the explicit mapping and add a regression test that asserts the target filenames.
- [Raster edits reduce legibility or alter the established style] -> Edit from the provided artwork, produce lossless WebP, and review the generated book pages at reader scale.
- [Figure metadata or site output becomes stale] -> Rebuild the English manifest, run figure checks, build the site, and run site-render tests.
- [A later change needs rollback] -> Revert the three target PNG/WebP pairs and the mapping test; no chapter-reference migration is required.
- [Before and after evidence is incomparable] -> Use the same built-reader routes, browser engine, viewport, full-page setting, and figure-specific screenshot names for both captures.

## Migration Plan

1. Stage and validate the three Jira source attachments.
2. Produce and review the updated target PNG/WebP pairs.
3. Rebuild the English manifest and run automated and visual validation.
4. Capture updated screenshots using the baseline capture settings and submit both evidence sets together for review.
5. Publish through the normal site build; do not edit generated assets directly.
6. If validation or review fails, restore the prior target asset pairs and rerun the build.

## Open Questions

- None. The approved interpretation is that Jira's low-numbered filenames are source filenames, while the online figure numbers determine the repository target filenames.
