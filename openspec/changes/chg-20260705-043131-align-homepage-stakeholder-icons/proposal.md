## Why

The homepage stakeholder cards currently point at a repo-owned SVG set that no longer matches the approved screenshot reference. The mismatch is not limited to CSS placement: several icons use different silhouettes, stroke rhythm, and internal whitespace, so the section cannot reach pixel-level alignment through offsets alone.

The user has now supplied a concrete PNG source icon package under `/Users/edison/Downloads/Project - Africa_Book/icons_pixel_replica_ultra_crisp_png_all/`. We need a narrow repo-owned change that imports those six stakeholder PNGs into the project, aligns the verification baseline to that source set, and locks the result with regression checks so future homepage tweaks do not reintroduce drift.

## What Changes

- Import the six homepage stakeholder PNGs from the supplied local source package instead of continuing to tune or redraw the current mismatched shapes.
- Align the stakeholder icon baseline around the imported source set's raster geometry, transparent padding, and single-color blue line style so the cards render the provided artwork consistently inside the fixed homepage layout.
- Keep the existing stakeholder card markup, fixed `120px` card width, and desktop six-column layout contract, changing CSS only as needed to double the displayed icon size, equalize visual weight, and keep every icon center on the same horizontal line.
- Add focused verification for stakeholder icon geometry so the visible PNG bounds stay stable after future edits.

## Capabilities

### New Capabilities
- `homepage-stakeholder-icon-alignment`: The homepage stakeholder cards render the imported stakeholder source PNG set and preserve stable icon geometry, doubled display sizing, and a shared icon centerline inside the fixed `120px`-wide card grid.

### Modified Capabilities
- None.

## Impact

- Affected source generation: `scripts/shared/homepage-content.mjs`
- Affected landing styles: `assets/css/landing.discovery.css`
- Affected visual assets: `assets/icons/stakeholders/*.png`
- Affected verification: `scripts/test-site-render.sh` and a new targeted icon-geometry test
- Affected generated outputs after rebuild: `index.html`, localized homepage outputs, and `public/assets/icons/stakeholders/*`
