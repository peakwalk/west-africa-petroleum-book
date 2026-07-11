## Context

The landing shell currently hard-codes `assets/images/upstream-atlas-favicon.png?v=2` for all three icon relationships: browser favicon, shortcut icon, and Apple touch icon. The source file is `240x256` and about `45KB`. That is oversized for the tab-icon use case, while Apple touch icons still benefit from a larger square PNG.

This change should stay narrow. It only needs to improve landing-shell icon delivery, preserve PNG compatibility, and avoid unrelated changes to homepage visuals or book-reader behavior.

## Goals / Non-Goals

**Goals:**
- Reduce favicon bytes loaded by landing routes during normal browser navigation.
- Keep Apple touch icon delivery explicit and separate from the small tab icon.
- Keep the change limited to landing-shell markup, favicon assets, and landing verification.

**Non-Goals:**
- Switch favicon delivery to WebP.
- Redesign the icon artwork.
- Change mdBook reader favicon delivery in `theme/index.hbs` as part of this landing-scoped step.

## Decisions

### Decision: Add two landing-scoped PNG derivatives from the existing source icon
The repo will keep `assets/images/upstream-atlas-favicon.png` as the editable source and add:
- `assets/images/upstream-atlas-favicon-32.png` for browser tab and shortcut icon use
- `assets/images/upstream-atlas-apple-touch-icon.png` for Apple touch icon use

The new assets will be derived from the existing source icon, padded to a square canvas, and stripped of unnecessary metadata.

Alternative considered:
- Keep one shared PNG and only recompress it. Rejected because the browser-tab path still does not need a `240x256` payload.

### Decision: Update only the shared landing head generator
`scripts/shared/landing-shell.mjs` will emit the smaller favicon path for `rel="icon"` and `rel="shortcut icon"` and the dedicated larger PNG for `rel="apple-touch-icon"`. This improves all landing, legal, and chapters shell pages in one place without broadening into the book reader theme.

Alternative considered:
- Update both landing shell and book theme in the same step. Rejected for now to keep the change aligned with the landing-page scope the user asked about.

### Decision: Lock the new contract in tests and size caps
Regression tests will assert the new favicon and touch-icon paths in generated landing output, and built-site checks will enforce explicit maximum sizes for both new PNG derivatives.

Alternative considered:
- Rely only on asset presence checks. Rejected because path regressions back to the old oversized favicon would still pass.

## Risks / Trade-offs

- [Two assets replace one source path] -> Keep the original source file in the repo and derive both new files from it so updates remain simple.
- [Landing and book pages temporarily diverge in favicon delivery] -> Accept this because the user asked about landing pages; a follow-up can align the mdBook theme if needed.
- [Apple touch icon still costs bytes when requested] -> Accept this because it is not part of ordinary page-load behavior and remains smaller than the old all-purpose asset path.

## Migration Plan

1. Add failing landing-shell tests for the split favicon contract.
2. Generate the new `32x32` favicon and `180x180` Apple touch icon assets from the existing source PNG.
3. Update `scripts/shared/landing-shell.mjs` to reference the split assets.
4. Rebuild the site, run landing-focused verification, and validate the OpenSpec change.
5. If rollback is needed, revert the landing shell to the original single favicon path and remove the derivative assets.

## Open Questions

- None for this change.
