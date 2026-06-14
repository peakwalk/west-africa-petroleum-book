## 1. Search template and verification updates

- [x] 1.1 Update `theme/index.hbs` to add the clear button, keep the book search ids, and stop loading `searcher.js`
- [x] 1.2 Update `scripts/test-site-render.sh` to assert the new search markup, CSS hooks, JS hooks, and the absence of `searcher.js`

## 2. Custom SearchBox implementation

- [x] 2.1 Replace the current toolbar search glue in `theme/custom.js` with a theme-owned state controller that lazy-loads `searchindex.js` and filters `title`, `body`, and `breadcrumbs`
- [x] 2.2 Render highlighted result rows, result count, empty state, clear-button behavior, outside-click dismissal, and keyboard navigation from `theme/custom.js`
- [x] 2.3 Preserve highlight-on-navigation by appending a `highlight` query param to result links and applying `Mark` on destination load

## 3. Styling and verification

- [x] 3.1 Update `theme/custom.css` so the search slot expands through JS-controlled focus state and the results panel is an absolute dropdown under the input
- [x] 3.2 Add minimal CSS support for result rows, active state, icon chips, excerpt text, and empty state
- [x] 3.3 Keep a visible search toggle on narrow screens and reveal the toolbar search slot as a header overlay when mobile search opens
- [x] 3.4 Run `npm run test:site` and fix any regressions until the build and render assertions pass
