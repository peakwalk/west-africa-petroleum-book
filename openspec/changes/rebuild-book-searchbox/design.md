## Context

The `/book/` reader already reshapes mdBook's toolbar search into a header slot through `theme/custom.js`, but the actual searching and result rendering are still owned by mdBook's generated `searcher.js`. That split makes the current search UX hard to control because the custom theme moves DOM nodes while the generated script still assumes ownership of focus, result overlay placement, and keyboard behavior.

The requested interaction model is narrower and more deterministic than mdBook's default implementation:

- results are filtered from local data in real time
- the panel only appears while the input is focused and the query is non-empty
- clearing the query must not blur the input
- outside clicks must close the panel without relying on `blur`
- the dropdown should render directly below the input, not in a detached fixed overlay

The existing mdBook index already contains the fields we need: `title`, `body`, and `breadcrumbs`. In this repo, `breadcrumbs` is the closest equivalent to the prompt's section/category field, so there is no need to alter index generation.

## Goals / Non-Goals

**Goals:**
- Keep mdBook's generated `searchindex.js` as the search data source.
- Replace mdBook `searcher.js` behavior with a theme-owned `SearchBox`.
- Match the approved prompt behavior for state, filtering, dismissal, clear action, highlighting, and optional keyboard support.
- Keep the implementation scoped to theme source files and render assertions.

**Non-Goals:**
- Rebuild search as a server-backed or fuzzy-ranked feature.
- Change mdBook's search index generation pipeline.
- Redesign the broader reader toolbar or chapter layout outside the search control.
- Introduce a framework runtime such as React just for search.

## Decisions

### 1. Remove `searcher.js` from the theme and replace it in `theme/custom.js`

`searcher.js` owns DOM, focus, keyboard handling, URL state, and result markup. Patching around it would leave two controllers fighting over the same nodes. The safer approach is to stop loading `searcher.js` from `theme/index.hbs` and implement the required `SearchBox` logic directly in `theme/custom.js`, where the rest of the reader shell behavior already lives.

Alternative considered:
- Keep `searcher.js` and layer event listeners on top of it. Rejected because it would preserve incompatible `keyup`, `keydown`, and result-overlay assumptions, making bugs around focus and selection likely.

### 2. Use `searchindex.js` document payloads as plain local records

We do not need Elasticlunr's ranked search API to satisfy the prompt. The generated `window.search.index.documentStore.docs` data already exposes `title`, `body`, and `breadcrumbs`, and the repo only indexes about a hundred entries. The custom search box will lazy-load `searchindex.js`, convert those docs into plain records, and perform case-insensitive local filtering.

Alternative considered:
- Reuse Elasticlunr ranking from the serialized index. Rejected because the prompt asks for deterministic filtering behavior, not ranked full-text search, and because plain filtering is easier to debug and adapt.

### 3. Treat `breadcrumbs` as the section/category label

The prompt asks for matches against section/category fields and for a section label in each result. This repo's mdBook index already stores hierarchy in `breadcrumbs`, for example `Chapter 1 ... » 1.1.3- Main challenges`. The custom result renderer will use `breadcrumbs` both as a searchable field and as the visible section label.

Alternative considered:
- Generate a new dedicated category field. Rejected because it would widen the change into the mdBook indexing layer without improving the shipped UX enough to justify the scope.

### 4. Keep page highlight support through `mark.min.js`

Even though URL-managed search state is not required by the prompt, highlighting the selected query on the destination page is a useful carry-over from the current behavior. Result links will append `?highlight=<query>` and `theme/custom.js` will apply `Mark` to the reader content on load when that param exists.

Alternative considered:
- Drop highlight behavior entirely. Rejected because the repo already ships `mark.min.js`, and preserving on-page emphasis is low-cost.

## Risks / Trade-offs

- [Local substring filtering is simpler than ranked search] -> Accept the trade-off because the index is small and the prompt explicitly prioritizes interaction logic over advanced relevance ranking.
- [The search index script is large] -> Lazy-load `searchindex.js` only when search is first used, and cache the parsed records after the first load.
- [Removing `searcher.js` can regress existing keyboard shortcuts] -> Re-implement `/`, `s`, `Escape`, Arrow, and `Enter` behaviors inside the custom controller and cover them with source-level assertions.
- [Search styling already has theme-specific overrides] -> Keep selector changes scoped to the existing `toolbar-search-slot` structure rather than inventing a new shell.

## Migration Plan

1. Update search markup in `theme/index.hbs` to include a clear button and to stop loading `searcher.js`.
2. Replace the current search-slot glue in `theme/custom.js` with a theme-owned `SearchBox` controller that loads local docs, filters, renders, dismisses, and highlights.
3. Update `theme/custom.css` so the input can widen via state and the results panel is an absolute dropdown below the input.
4. Update `scripts/test-site-render.sh` to assert the new source markers and generated output.
5. Run `npm run test:site` to rebuild the site and verify the new search behavior contract.

## Open Questions

- None. The only ambiguous field mapping was section/category, and this change resolves it by using `breadcrumbs`.
