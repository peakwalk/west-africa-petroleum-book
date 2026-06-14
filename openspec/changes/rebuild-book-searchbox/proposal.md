## Why

The current book search experience is still driven by mdBook's default `searcher.js`, which renders a generic overlay and mixes search behavior with keyboard and URL management that does not match the approved `SearchBox` interaction model. We need a source-level implementation that keeps the local mdBook search index but rewrites the UX around focused filtering, explicit dismissal, highlighted results, and clear input behavior.

## What Changes

- Replace the default mdBook `searcher.js` wiring in the book template with a custom `SearchBox` implementation owned by `theme/custom.js`.
- Keep `searchindex.js` as the local data source, but filter against `title`, `body`, and `breadcrumbs` in real time on the client.
- Add explicit `focused`, clear-button, outside-click dismissal, result-count, empty-state, and highlighted-result behaviors to the book toolbar search UI.
- Reposition the results panel as an absolutely positioned dropdown beneath the toolbar input instead of the current fixed overlay root behavior.
- Update site render assertions so the source theme and generated `/public/book` output verify the new search contract.

## Capabilities

### New Capabilities
- `book-searchbox`: A custom toolbar search box for `/book/` pages that filters local mdBook index data with focused dropdown interactions and highlighted results.

### Modified Capabilities
- None.

## Impact

- Affected source files: `theme/index.hbs`, `theme/custom.js`, `theme/custom.css`, `scripts/test-site-render.sh`
- Generated output affected through build: `public/book/*`
- No new runtime dependencies
- mdBook remains the content and index generation engine
