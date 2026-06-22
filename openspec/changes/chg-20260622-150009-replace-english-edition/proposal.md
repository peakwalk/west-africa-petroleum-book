## Why

The newly added English manuscript is not a line edit of the current English edition. It is a replacement book with a much larger body, a different left-navigation shape, and a different chapter system. The current English workspace still encodes the retired six-chapter structure, and `python3 scripts/check_docx_parity.py --edition en --docx <new-manuscript>` currently reports zero extracted outline/body content for every English chapter, which shows the old anchor model no longer matches the source manuscript.

We need a controlled English-only replacement plan now so the repo can adopt the new English manuscript as the canonical source without mutating the French edition. The French navigation, content, figures, and manuscript aliases must remain unchanged throughout the change.

## What Changes

- Promote the new English DOCX/PDF pair to the candidate canonical manuscript for the English edition only, while keeping the French manuscript aliases and French content unchanged.
- Rebuild the English `SUMMARY.md`, chapter tree, front matter, back matter, and reader sidebar contract from the new English manuscript's actual table of contents instead of preserving the retired six-chapter shell.
- Update the English DOCX parity and extraction workflow so validation understands the new English chapter anchors, prefatory material, and back matter.
- Regenerate the English figure inventory, figure manifest, and published figure assets from the new English manuscripts, and retire English-only legacy figures that no longer exist in the replacement source.
- Cut over the English manuscript aliases only after staged validation passes, with an English-only rollback path that does not touch French files.

## Capabilities

### New Capabilities
- `english-edition-replacement`: Replace the English edition from a new canonical manuscript by rebuilding English navigation, chapter content, and figure assets while leaving the French edition untouched.

### Modified Capabilities
- None.

## Impact

- Affected code is expected to include `config/editions.json`, `resources/editions/en/reference.docx`, `resources/editions/en/reference.pdf`, `editions/en/content/SUMMARY.md`, `editions/en/content/chapters/*`, `editions/en/content/images/*`, and shared validation/build scripts such as `scripts/docx_parity/*`, `scripts/check_docx_parity.py`, `scripts/build_docx_figure_manifest.py`, and figure render helpers.
- The change intentionally excludes edits to `editions/fr/**`, `resources/editions/fr/reference.*`, and French reader navigation/content.
- Build and validation work will focus on English cutover safety plus French regression protection for shared parser changes; no new runtime dependency is required.
