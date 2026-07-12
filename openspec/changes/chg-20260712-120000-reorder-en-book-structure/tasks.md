## 1. English source structure

- [x] 1.1 Reorder the English summary, retain Chapter 5 in Part II, and apply the approved Part II and Part III labels.
- [x] 1.2 Apply the 10→7, 7→8, 8→9, and 9→10 map to affected English chapter titles, numbered headings, and equation identifiers without renaming chapter files.

## 2. References and generated-site inputs

- [x] 2.1 Update the English manual table of contents and the figure, table, and equation indexes so headings and anchors match the new number map and order.
- [x] 2.2 Update intentional English prose references and the chapter-library part-label map; leave stable route maps and the French edition unchanged.

## 3. Verification

- [x] 3.1 Build the site and inspect generated English navigation, chapter metadata, manual-index links, and stable chapter routes.
- [x] 3.2 Run the narrowest useful English DOCX-parity check, run the site regression suite, and review the final path-scoped diff for unintended source or generated-file edits.

## 4. Canonical chapter URL migration

- [x] 4.1 Rename the four English chapter source files so their filenames match their revised display numbers, then update every English source link and test reference.
- [x] 4.2 Update English-to-French route maps and generate legacy English chapter redirect pages outside the sitemap.
- [x] 4.3 Build the site and verify canonical URLs, legacy redirects, metadata, sitemap exclusion, and relevant regression checks.

## 5. Reference DOCX synchronization

- [x] 5.1 Directly edit the English reference DOCX OOXML package to reorder complete Chapter 7–10 blocks and apply the approved number map, without opening Microsoft Word.
- [x] 5.2 Validate the edited package structure and run English DOCX parity and formula-coverage checks.
- [x] 5.3 Render the synchronized DOCX using the packaged renderer and inspect representative pages for layout regressions.
