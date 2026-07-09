## Why

The current landing page still mixes several low-fidelity legacy icon assets across the English homepage and the French compatibility homepage. Some sections already use SVG containers, but the rendered assets are inconsistent in source, metaphor, and output quality, and the English topic-reference cards still point to PNG files instead of SVGs.

The user has now supplied a 26-file SVG icon pack and wants the corresponding 26 landing-page icon slots to use those exact files. We need a narrow change that swaps those mapped assets without redesigning landing-page copy or structure.

## What Changes

- Replace the corresponding 26 landing-page icon assets with the supplied SVG pack from `/Users/edison/Downloads/Project - Africa_Book/Upstream Atlas Version 2 Website - Icons (from Matt)` while preserving the existing repo asset paths.
- Switch the English topic-reference card helper from `.png` topic icon references to `.svg` references.
- Leave non-corresponding landing-page icon surfaces unchanged.
- Update landing-page verification assertions so generated output checks the supplied hero and topic SVG files.

## Capabilities

### New Capabilities
- `landing-page-icon-assets`: Generated landing pages render the supplied 26-file SVG icon pack for the mapped hero, stakeholder, search-scope, and topic icon slots.

### Modified Capabilities
- None.

## Impact

- Affected source generation: `scripts/shared/homepage-topic-reference.mjs`
- Affected landing source HTML: `editions/fr/site/index-main.html`
- Affected asset roots: `assets/icons/homepage/`, `assets/icons/homepage-sprite.svg`, `assets/icons/search-scope/`, `assets/icons/stakeholders/`, `assets/icons/topics/`
- Affected verification: `scripts/test-site-render.sh`
- Affected generated outputs after rebuild: `public/index.html`, `public/fr/index.html`, and copied `public/assets/icons/*`
