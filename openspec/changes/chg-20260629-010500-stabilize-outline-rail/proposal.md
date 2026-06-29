## Why

The desktop reader currently decides outline-rail preservation in two separate places, which already allowed `chapter-11-general-conclusion.html` to drift into a different left margin than comparable chapter pages. The same area also depends on fragile runtime figure detection, so small caption-format changes can silently remove outline content and reintroduce the layout regression.

## What Changes

- Centralize book page variant classification so generated book pages carry the correct preserve-outline-rail body classes without a runtime classifier.
- Add a site-render regression check that simulates runtime outline visibility and fails when a real chapter page would collapse to an empty outline without an intentional preserved rail.
- Harden runtime figure caption annotation so figure cards can still be derived from image alt labels and short adjacent caption paragraphs when explicit `Figure N ...` text is missing or partially degraded.

## Capabilities

### New Capabilities
- `reader-outline-rail-stability`: Keep desktop reader content-column alignment stable across boot, hydration, and runtime figure annotation changes.

### Modified Capabilities
- None.

## Impact

- Affected code: `theme/index.hbs`, `theme/custom.js`, `scripts/localize_reader_shell.mjs`, new shared script helper(s), and `scripts/test-site-render.sh`
- Validation: theme/source assertions plus `npm run build:site` and `npm run test:site`
- Risk surface: desktop reader layout, runtime outline visibility, and figure caption parsing for English/French chapters
