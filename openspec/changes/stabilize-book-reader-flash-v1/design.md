## Context

The current left-rail navigation uses two separate runtime projection paths:

- an inline `bootstrapSidebarProjection()` script in `theme/index.hbs`
- a second `installSidebarProjection()` path in `theme/custom.js`

Both rebuild `.reader-sidebar-projection` after page parse, and both rely on runtime geometry to reconcile sidebar scroll position. At the same time, layout-affecting transitions on `.reader-main` and `.book-progress` are enabled during boot, which makes any late left-offset or projection correction visible to the reader.

The repo already has a stable generated navigation source: `public/book/toc.html`. That makes this a good candidate for a build-time projection instead of a client-time reconstruction.

## Goals / Non-Goals

**Goals:**
- Ensure generated book pages already contain final sidebar projection markup before client JavaScript runs.
- Remove runtime sidebar reprojection from both the template and `theme/custom.js`.
- Prevent first-paint layout transitions from animating reader geometry during boot.
- Preserve the current `#mdbook-reader-scroll` model and the existing outline/progress logic in `v1`.

**Non-Goals:**
- Revert the reader back to native document scrolling in this change.
- Rewrite hash navigation, progress tracking, or outline scroll-spy around a new scroll root.
- Redesign sidebar visual language beyond what is needed to stabilize boot behavior.
- Replace mdBook as the navigation source of truth.

## Decisions

### 1. Use a repo-owned post-build injector instead of changing mdBook internals

The repo already performs post-build work through scripts like `strip_mdbook_onunload.mjs` and `build_reader_page_meta.mjs`. Adding `scripts/build_static_reader_sidebar.mjs` follows the same pattern and keeps this change scoped to repo-owned build tooling.

Alternative considered:
- Patch mdBook output generation directly. Rejected because it would widen the change beyond this repo and make the navigation contract harder to iterate on locally.

### 2. Keep the current scroll model in `v1`

The largest regression surface is the existing internal scroller bridge. It is currently entangled with hash scrolling, progress calculations, and scroll-dependent UI. `v1` therefore stabilizes first paint without touching `installInternalScrollerBridge()`.

Alternative considered:
- Remove the scroll bridge as part of the same fix. Rejected because it would combine two high-risk changes and make regressions harder to isolate.

### 3. Preserve sidebar viewport position with a simpler contract

The old projection logic stores row-relative offsets and then mutates the visible rail after reprojection. In `v1`, the reader should persist a simpler `reader-sidebar-scroll-top` value and restore it without rebuilding sidebar rows. This keeps the active region visible without reintroducing a projection-time geometry calculation.

Alternative considered:
- Drop all sidebar position persistence. Rejected because it would create a new visible regression on lower chapters and back matter pages.

### 4. Disable layout transitions during boot through a template-owned state class

The current motion on `padding-inline-start`, `width`, and `margin-inline-start` is useful after the reader is interactive, but not during first paint. A boot-only body class gives a narrow, reversible way to suppress those transitions until initialization is complete.

Alternative considered:
- Remove the transitions entirely. Rejected because the motion remains useful for user-triggered sidebar state changes once the page is stable.

## Risks / Trade-offs

- [Static injection could drift from mdBook TOC output] -> Keep the injector parser narrowly aligned to the generated `toc.html` structure and lock it with render assertions.
- [Early sidebar scroll restore could still move visible content if done too late] -> Perform restore from a small template-owned script tied to already-rendered projected markup instead of waiting for `DOMContentLoaded`.
- [Keeping the internal scroller preserves some technical debt] -> Accept in `v1` because eliminating the visible flash is the immediate user-facing goal; treat scroll-model cleanup as a follow-up change.
- [Generated output size increases because sidebar HTML is duplicated into chapter pages] -> Accept because the number of chapters is small and the stability gain is worth the extra markup in this repo.
