## Why

The reader already annotates numbered equations and exposes them in the right-hand outline rail, but the front matter only publishes static indexes for figures and tables. Readers who want to browse equations globally cannot navigate to a dedicated equation index from the front matter or chapter library.

We need a first-class `List of Equations` page that sits beside `List of Tables`, uses the same reference-index presentation, and links only to numbered equations that are intentionally published as navigable reference surfaces.

## What Changes

- Add a front-matter `List of Equations` page to the English and French editions immediately after `List of Tables`.
- Reuse the existing numbered-equation anchor contract so the new page links to stable `#formula-*` targets rather than introducing a second formula indexing scheme.
- Extend the reader front-matter page-variant logic and release assertions so the new equation index behaves like the existing figure/table indexes.

## Impact

- Affected files are expected to include `editions/*/content/SUMMARY.md`, edition-local `list-of-equations.md` pages, `theme/index.hbs`, `theme/custom.js`, and site tests.
- The change does not alter equation extraction rules or renumber existing equations; it only exposes already-numbered equations through a front-matter index.
