## Why

The current `/book/` reader still rebuilds its left sidebar after the browser has already painted the page, and it also animates layout-affecting geometry during boot. That combination produces a visible flash when readers navigate between chapters from the left rail, which makes the book feel unstable and unfinished.

## What Changes

- Move the final `.reader-sidebar-projection` markup from runtime JavaScript construction to a repo-owned post-build injection step that reads `public/book/toc.html`.
- Remove the inline and `theme/custom.js` runtime sidebar reprojection paths once static sidebar injection is in place.
- Add a boot-state layout contract so first-paint geometry transitions are disabled until the reader shell is ready.
- Preserve the current `#mdbook-reader-scroll` model in this release; do not remove the internal scroll bridge yet.
- Update render assertions so source files and generated `/public/book` output lock the new static-sidebar and boot-stability contract.

## Capabilities

### New Capabilities
- `book-reader-flash-stability`: The `/book/` reader provides a static first-paint sidebar contract that avoids visible layout flash during left-rail navigation while preserving the current scroll model.

### Modified Capabilities
- None.

## Impact

- Affected source files: `theme/index.hbs`, `theme/custom.js`, `theme/custom.css`, `scripts/test-site-render.sh`, `scripts/preview.sh`, `package.json`
- New build tooling: `scripts/build_static_reader_sidebar.mjs`
- Generated output affected through build: `public/book/index.html`, `public/book/chapters/*.html`
- No new runtime dependencies
- mdBook remains the navigation source of truth and still owns `toc.html` generation
