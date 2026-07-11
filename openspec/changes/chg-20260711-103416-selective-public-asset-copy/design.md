## Context

The repo now has a much smaller source asset set after the earlier cleanup passes, but `scripts/build_site.mjs` still republishes more than the runtime needs because it copies the full `assets/` tree into both locale outputs.

That full-copy behavior creates two different waste patterns:
- source-only files still ship into public outputs, such as `upstream-atlas-hero-book.png` and the retained graywhite PNG backups;
- English-homepage-only assets still ship into `public/fr/assets/`, including the homepage cover WebP, the homepage map panel SVG, and the cropped WebP icon set.
- English-root outputs still carry icon groups that the generated pages no longer reference directly, including `country-flags.svg`, the published `stakeholders/` and `topics/` directories, and the entire `homepage/` icon directory.

The change should stay narrow. It should alter only the final asset-copy phase, preserve current generated markup and CSS contracts, and keep the active book-theme image chain intact.

## Goals / Non-Goals

**Goals:**
- Stop copying source-only images into public outputs.
- Stop copying English-homepage-only assets into `public/fr/assets/`.
- Preserve all current runtime asset references for English landing, French landing, and both book outputs.

**Non-Goals:**
- Redesign landing or book pages.
- Replace asset references in generated HTML/CSS.
- Optimize every public asset directory to the theoretical minimum in this pass.

## Decisions

### Decision: Use explicit shared and English-only asset manifests
`scripts/build_site.mjs` will define:
- a shared asset manifest copied to both `public/assets/` and `public/fr/assets/`;
- an English-only manifest copied only to `public/assets/`.

The shared manifest will keep the runtime assets required by:
- both landing shells,
- both legal/chapter landing pages,
- both book outputs.

The English-only manifest will hold assets only the English homepage needs, such as:
- `assets/images/homepage-west-africa-map-panel.svg`
- `assets/images/upstream-atlas-hero-book.webp`
- `assets/icons/homepage-cropped/*.webp`

Alternative considered:
- Parse generated markup and CSS to derive a fully automatic asset manifest. Rejected for this pass because it adds more moving parts and higher regression risk than a small explicit manifest.

### Decision: Stop publishing source-only image backups
Source assets kept only for editing or regeneration, such as `upstream-atlas-hero-book.png` and `prototype-hero-graywhite-left.png`, will remain in the repo but will no longer be copied into public outputs.

Alternative considered:
- Delete those source files from the repo. Rejected because they are still retained as editable sources and this change is only about publication scope.

### Decision: Remove root-only icon directories that no generated page references
The English root output will stop publishing:
- `assets/icons/country-flags.svg`
- `assets/icons/homepage/*`
- `assets/icons/stakeholders/*`
- `assets/icons/topics/*`

The French output will keep only the six homepage SVG icons its landing page still references directly and will stop publishing the unused remainder of `assets/icons/homepage/`.

Alternative considered:
- Keep the root icon directories because older assertions still expected them. Rejected because those assertions describe historical copying behavior rather than runtime need.

## Risks / Trade-offs

- [The explicit manifest could drift from future runtime references] -> Accept this and add site-render assertions for the omission contract.
- [The explicit manifest must now encode a smaller subset of French homepage SVG icons] -> Accept this because the runtime references are concrete and limited.

## Migration Plan

1. Add failing assertions for source-only public images and French-tree English-homepage assets.
2. Implement selective shared vs English-only asset copying in `scripts/build_site.mjs`.
3. Rebuild the site and verify both locale trees still satisfy current page contracts.
4. Validate the OpenSpec change artifacts.

## Open Questions

- None for this change.
