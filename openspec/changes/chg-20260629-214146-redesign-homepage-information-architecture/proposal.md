## Why

The current homepage still reflects an older information model. It mixes orientation, chapter discovery, country discovery, and generic resource promotion in a way that makes first-time visitors work too hard to answer basic questions: what Upstream Atlas is, what geography it covers, where to enter by country, where to enter by topic, how to search the book, and how current the content is.

The UA-11 Version 2 materials in `resources/version2/` redefine the homepage around a simpler first-principles goal: establish Upstream Atlas as the leading independent petroleum reference for West Africa by prioritizing clarity, credibility, fast navigation, and long-term scalability. To implement that direction safely in this repo, we need a repo-owned OpenSpec change that turns the redesign into an explicit information architecture, scope boundary, and rollout plan instead of a one-off template rewrite.

## What Changes

- Rebuild the homepage information architecture around five mutually exclusive and collectively exhaustive user intents: orientation, country discovery, topic discovery, book search, and freshness/contact signals.
- Update the shared landing shell so the top navigation removes obsolete `Resources` and `About` entries, keeps `Countries` and `Chapters`, adds direct `Search` and `Contact` actions, and remains locale-safe across English and French builds.
- Replace the current English homepage body with the Version 2 structure: revised hero, `Coverage Across West Africa` country-card grid, clickable West Africa political map, `Browse by Topic`, `Search Upstream Atlas`, `Latest Updates`, `Current Edition`, `Topics Covered`, `Future Development`, and expanded footer coverage.
- Centralize homepage-controlled data such as country metadata, country deep links, topic destinations, latest updates, and footer coverage copy so the redesign does not scatter content across templates and scripts.
- Reuse the existing static mdBook routes and search index for chapter/topic/search entry points; this phase does not introduce a new backend, database, or separate search service.
- Roll out the full body redesign on the English homepage first, while keeping the French homepage compatible through shared shell and routing updates. A full French body redesign is explicitly out of scope for this change.

## Capabilities

### New Capabilities
- `homepage-information-architecture`: The public homepage provides a clear, scalable, and static-build-friendly information architecture for entering Upstream Atlas by country, by topic, and by book search while reinforcing trust, freshness, and contact paths.

### Modified Capabilities
- None.

## Impact

- Affected landing-page sources are expected to include `editions/en/site/index-main.html` and `editions/fr/site/index-main.html`.
- Affected generation and shared-shell code is expected to include `scripts/generate-index-page.mjs` and `scripts/shared/landing-shell.mjs`.
- Affected presentation styles are expected to include `assets/css/landing.css`.
- Affected verification is expected to include `scripts/test-site-render.sh` and targeted site-render assertions.
- Existing mdBook routes and search assets remain the destination surface; this change should not add new runtime infrastructure.
