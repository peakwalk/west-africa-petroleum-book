## Context

The landing homepage feature cards, audience cards, and country signal rows now reference only the WebP files under `assets/icons/homepage-cropped/`. The PNG counterparts are not referenced by page generators, styles, or current verification beyond assertions that the HTML does not use them.

Because `scripts/build_site.mjs` copies the whole `assets/` tree into both locale outputs, the ten unused PNG files still ship into `public/assets/icons/homepage-cropped/` and `public/fr/assets/icons/homepage-cropped/`. Together they add about `115KB` to the source tree and about `230KB` to the two built public trees.

The directory README is also stale. It still describes the PNGs as first-class production assets even though the current landing contract uses WebP.

## Goals / Non-Goals

**Goals:**
- Remove the unused cropped-icon PNG variants from source and built landing assets.
- Keep the WebP assets untouched as the active landing contract.
- Align the local README with the actual asset format in use.

**Non-Goals:**
- Redesign or regenerate the cropped icon artwork.
- Replace the existing WebP icon set with SVG or another format.
- Change homepage markup or CSS selectors for the icon surfaces.

## Decisions

### Decision: Retire only the unused PNG icon copies
This change removes the ten `.png` files from `assets/icons/homepage-cropped/` and leaves the `.webp` files in place.

Alternative considered:
- Keep the PNG files as archival design sources. Rejected because they are not part of the runtime contract, they are duplicated into both public trees, and there is no current generation step that depends on them.

### Decision: Update directory documentation instead of leaving stale format guidance
`assets/icons/homepage-cropped/README.md` will describe the WebP files as the current production assets and note that control icons still belong in the SVG sprite. A Chinese companion file will be added alongside it to satisfy repo documentation-localization rules.

Alternative considered:
- Leave the README untouched. Rejected because it would immediately contradict the source tree after deleting the PNG files.

### Decision: Guard absence in source and built outputs
Add test coverage so the PNG variants must stay absent from `assets/icons/homepage-cropped/`, `public/assets/icons/homepage-cropped/`, and `public/fr/assets/icons/homepage-cropped/`.

Alternative considered:
- Rely only on HTML non-reference assertions. Rejected because the build copies the whole asset tree, so unused files could still ship silently.

## Risks / Trade-offs

- [The PNGs could be useful for future manual re-export work] -> Accept this because the repo already keeps the active WebP outputs and the removed files have no current automated dependency.
- [README wording now becomes format-specific] -> Accept this because accurate documentation is better than preserving obsolete format guidance.

## Migration Plan

1. Add failing regression checks for the cropped-icon PNG absence contract.
2. Update the cropped-icon README files to describe the WebP contract.
3. Delete the PNG icon copies from source.
4. Rebuild the site so the PNGs disappear from both public asset trees.
5. Run targeted tests, site verification, and OpenSpec validation.

## Open Questions

- None for this change.
