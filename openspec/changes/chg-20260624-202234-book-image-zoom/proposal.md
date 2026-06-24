## Why

The current `/book/` reader renders figures at reading width only. Dense charts, SVG diagrams, and multi-panel figures become hard to inspect, and the custom in-page viewer path has proven harder to stabilize than its value justifies.

## What Changes

- Add a lightweight runtime enhancement for body figure cards in the `/book/` reader.
- Reuse the existing generated figure-card markup so the behavior works for single-image and multi-image figures without changing chapter Markdown or figure manifests.
- Open the clicked figure asset in a new browser tab and rely on the browser's built-in image viewing, pan, and zoom behavior.
- Keep keyboard-accessible activation for eligible figure images.
- Keep the enhancement scoped to `.reader-article .figure-card img`; do not apply it to cover, navigation, landing-page, or decorative images.
- Remove the custom overlay viewer implementation and the vendored pan/zoom dependency.

## Capabilities

### New Capabilities
- `book-reader-image-zoom`: The `/book/` reader lets users inspect body figure images by opening the original asset in a new browser tab, without affecting non-body images.

### Modified Capabilities
- None.

## Impact

- Affected source files: `editions/en/book.toml`, `editions/fr/book.toml`, `theme/custom.js`, `theme/custom.css`, `tests/test_theme_custom_css.py`, `scripts/test-site-render.sh`
- Generated output affected through runtime enhancement: `/book/chapters/*.html`
- Removes the checked-in browser dependency and returns to theme-local JavaScript only
- No changes to edition chapter Markdown, figure manifests, or published asset naming are required for this behavior
