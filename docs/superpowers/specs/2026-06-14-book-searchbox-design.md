# Book SearchBox Design

**Date:** 2026-06-14

**Goal**

Replace the current mdBook-driven book search behavior with a theme-owned `SearchBox` that keeps the local search index but follows the approved prompt for state, filtering, clear behavior, outside-click dismissal, dropdown rendering, and highlighted results.

## Context

The current `/book/` toolbar search is only partially customized. `theme/custom.js` moves the search input into the toolbar slot, but mdBook's generated `searcher.js` still owns the actual search behavior and results panel. That split makes the UX hard to control and does not satisfy the requested interaction contract.

The repo already ships all data needed for a local search experience through `searchindex.js`, whose document store exposes `title`, `body`, and `breadcrumbs`. We can therefore keep mdBook as the indexing engine and rewrite only the toolbar search interaction layer.

## Scope

In scope:

- book toolbar search markup in `theme/index.hbs`
- book toolbar search behavior in `theme/custom.js`
- book toolbar search dropdown support styles in `theme/custom.css`
- render assertions in `scripts/test-site-render.sh`

Out of scope:

- mdBook index generation
- landing page search
- search ranking changes beyond deterministic local filtering
- broader reader-shell redesign unrelated to search

## Design Decisions

### 1. Theme-owned search controller

We will stop loading mdBook `searcher.js` from the template and replace it with a `SearchBox` controller inside `theme/custom.js`. That avoids conflicting event ownership and keeps the search implementation in the same source layer as the rest of the book shell behavior.

### 2. Plain local filtering over serialized docs

We will lazy-load `searchindex.js`, convert `window.search.index.documentStore.docs` into plain records, and filter them with case-insensitive matching across `title`, `body`, and `breadcrumbs`. `breadcrumbs` will also serve as the visible section/category label in results.

### 3. Prompt-aligned dropdown behavior

The search shell will own `query`, `focused`, `results`, and `activeIndex` state. The results dropdown will only render while focused and query-non-empty, will close from a document-level `mousedown` outside check, and will include a clear button that preserves focus.

### 4. Preserve destination-page highlight

Result links will append a `highlight` query parameter and `theme/custom.js` will use `Mark` to highlight the selected term on the destination page. This keeps a useful piece of the existing reader experience without reintroducing mdBook's full search URL workflow.

## Verification

- `npm run test:site`

## Risks

- Removing `searcher.js` can regress keyboard shortcuts if not fully reimplemented.
- The custom dropdown selectors must coexist cleanly with existing toolbar styles.
