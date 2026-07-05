## Context

The stakeholder card section is generated from `scripts/shared/homepage-content.mjs`, styled in `assets/css/landing.discovery.css`, and rendered with six standalone assets under `assets/icons/stakeholders/`. The current CSS already locks each card to a fixed `120px` box with per-icon sizing and offset variables, but the shipped SVG assets do not share consistent visible bounds. The user has now provided a local PNG source icon package at `/Users/edison/Downloads/Project - Africa_Book/icons_pixel_replica_ultra_crisp_png_all/`, which becomes the preferred visual source of truth for this change.

Before that source package arrived, the implementation direction was to redraw the icons from screenshots. With the new source set available, the narrower and more defensible move is to import the supplied PNGs directly, then make the repo verify and publish that exact set.

## Goals / Non-Goals

**Goals:**
- Import the six stakeholder icons from the supplied local source package as repo-owned transparent PNGs.
- Normalize project verification around the imported asset geometry so each stakeholder file keeps predictable visible bounds while the rendered row shares one horizontal icon centerline.
- Preserve the existing stakeholder card HTML contract, fixed `120px` width, and desktop six-column arrangement while allowing the displayed icon size to double and the card height to expand only as much as that larger icon slot requires.
- Add regression checks that catch visible-bound drift, not just missing files or HTML wiring.

**Non-Goals:**
- Redesign the stakeholder card layout, label copy, or overall decision-strip composition.
- Re-vectorize or redraw the supplied PNGs into a different production format.
- Rebuild the whole homepage icon system or unify every other homepage icon set in this change.
- Reconstruct another hand-drawn icon set when a user-approved source PNG package is already available.

## Decisions

### Decision: Import the provided PNG source files directly into the repo
The implementation will use the supplied local PNG source package as the stakeholder icon truth and copy those files into the repo-owned asset path. This respects the user's newer source-of-truth input, avoids a second hand-drawn approximation layer, and keeps the rendered cards aligned to the exact raster set the user approved.

Alternative considered:
- Keep the hand-redrawn SVG approximation built from screenshots. Rejected because the user later supplied a concrete icon source package and explicitly asked to use it directly.

### Decision: Normalize verification around the imported source set instead of rewriting the source geometry
The imported stakeholder PNGs keep their original `1024x1024` pixel dimensions and transparent padding. Rather than redrawing or vectorizing that geometry into a new house style, the repo will lock verification to the imported source set's trimmed visible bounds. CSS can still apply small optical corrections plus per-icon size equalization, but the imported asset itself remains primary.

Alternative considered:
- Rewrite the imported PNGs into a new SVG or `32x32` normalized set. Rejected because the user explicitly requested direct introduction of the supplied files, not a transformed derivative.

### Decision: Preserve the imported source pixel contract
The imported PNGs already encode the desired single-color navy line style, transparent background, and visible padding. Verification will preserve that source contract instead of recoloring, tracing, or recompositing the files during import.

Alternative considered:
- Recolor or trace the imported source into a new house style. Rejected because that would mean the project no longer ships the supplied source assets as-is.

### Decision: Lock geometry with rendered-bounds assertions
Verification will inspect each PNG at its fixed pixel size, trim transparent edges, and assert the resulting bounding box. This remains the narrowest automated proxy for what the browser effectively sees, and it adapts cleanly to the imported source set without requiring a separate SVG rasterization step.

Alternative considered:
- Assert only that the six PNG files exist and that the card CSS still uses the current size variables. Rejected because those checks can pass even when the visible icons drift away from the intended source set.

## Risks / Trade-offs

- [The imported source set uses a larger `1024x1024` raster canvas than the repo's previous `32x32` SVG set] -> Lock verification to trimmed visible bounds instead of raw placeholder-size assumptions.
- [The PNG source package ships multiple size variants] -> Standardize on `png_1024_transparent/` so the repo keeps the full-resolution transparent production assets without taking the larger `2048` payload.
- [The imported source files may still need small CSS optical correction once seen in the 120px cards] -> Keep CSS changes optional and minimal; only adjust after checking the real card render.
- [Exact bbox assertions can be brittle if the source package changes later] -> Keep the test scoped to these six icons and update expected boxes only when a deliberate source refresh is approved.
- [The current worktree already contains unrelated homepage edits] -> Limit file changes to the stakeholder assets, minimal CSS/test touch points, and the new OpenSpec change files.

## Migration Plan

1. Update the OpenSpec artifacts to record the direct-import source-package approach.
2. Add a failing geometry regression check aligned to the imported source PNGs.
3. Import the PNG assets from the supplied local source package and apply only the smallest required CSS adjustments if the rendered cards need them.
4. Rebuild the site outputs and run focused verification, including the geometry check and site render assertions.
5. If the import is unacceptable, roll back by reverting the six PNG assets, the stakeholder asset references, and the focused verification changes; no data migration is involved.

## Open Questions

- None. The user has explicitly chosen the direct-import PNG source package approach.
