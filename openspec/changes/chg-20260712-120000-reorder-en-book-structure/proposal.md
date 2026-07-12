## Why

The English reader currently introduces Petroleum Data Management as Chapter 10, after fiscal and governance material. UA-16 requires that chapter to follow Chapter 6 so readers encounter operational data management before the fiscal sequence.

## What Changes

- Reorder the English book so `chapter-10-petroleum-data-management-in-west-africa.md` follows Chapter 6 and is displayed as Chapter 7.
- Renumber the following English chapters and their numbered sections, manual indexes, and prose cross-references.
- Rename English Parts II and III to reflect the new sequence while retaining Chapter 5 in Part II so every existing chapter remains assigned to a part.
- Rename the affected English chapter files so canonical public URLs use their revised chapter numbers, then regenerate navigation, reader metadata, SEO, sitemap, and static chapter output.
- Generate compatibility redirect pages from the former chapter URLs to their corresponding canonical URLs.
- Synchronize the English source reference DOCX to the same Chapter 7–10 order and numbering by directly editing its OOXML package; do not open it in Microsoft Word.
- **BREAKING:** visible chapter numbers, canonical chapter URLs, and in-page numbered anchors change. Former chapter URLs remain available as client-side redirects.

## Capabilities

### New Capabilities

- `english-book-structure`: Maintains a coherent English chapter sequence, display numbering, and generated navigation after a chapter is moved.

### Modified Capabilities

- None.

## Impact

- English source: `editions/en/content/SUMMARY.md`, chapters 01 and 07–10, and the manual table, figure, table, and equation indexes.
- Generated-site inputs: English chapter metadata, canonical and cross-language route maps, and static legacy redirect generation.
- No French book content, figure asset, or `public/` build artifact is edited by this change. The Git-ignored English `resources/editions/en/reference.docx` is updated locally only to match the approved chapter sequence and number map; its external source must be distributed separately from this Git change.
