## Context

The reader preserves desktop outline-rail width for a small set of pages that intentionally hide or suppress visible outline content. That classification currently lives in both `theme/index.hbs` and `theme/custom.js`, so any path addition or removal can diverge between the boot pass and the hydrated pass. The reader also derives figure outline items at runtime, which means static HTML inspection alone does not reveal whether a page will have visible outline content once scripts run.

## Goals / Non-Goals

**Goals:**
- Use one shared source for desktop page-variant classification and stamp the result into generated HTML.
- Add a regression check that reasons about runtime outline visibility instead of only static markup.
- Make figure annotation resilient to minor caption-format drift without changing chapter source content.

**Non-Goals:**
- Rebuild the figure pipeline to emit canonical `<figure>` markup at build time.
- Replace the current preserve-outline-rail page list with a new metadata system.
- Change chapter copy or rebalance reader CSS tokens.

## Decisions

1. Create a shared `scripts/shared/book-page-variants.mjs` module and let `scripts/localize_reader_shell.mjs` stamp the resolved body classes into each generated book page.
   - This removes the extra runtime classifier entirely while keeping one authoritative preserve-outline-rail table.
   - Alternative considered: keep a runtime helper and inline only a reduced boot classifier. Rejected because it still duplicates classification between generated HTML and hydrated behavior.
2. Keep the explicit preserve-outline-rail list in the shared module.
   - This is the smallest safe fix because `chapter-11-general-conclusion.html` is a legitimate content page with no headings or figures, so it still needs an intentional exception.
   - Alternative considered: infer all preserved pages from content shape alone. Rejected because some intended exceptions have no runtime outline signal.
3. Add a site-render regression check that imports shared page-variant and outline-count logic instead of extracting functions from theme source strings.
   - This closes the current gap where path-list drift or caption-parser drift can silently change layout without failing validation, while avoiding a second copy of the algorithm in shell.
   - Alternative considered: only assert source strings. Rejected because source checks do not prove the generated book pages remain safe.
4. Harden `annotateFigureCaptions()` with an alt-label fallback that only promotes short, caption-like paragraphs directly following image blocks.
   - This captures degraded figure markup without over-classifying long narrative paragraphs as captions.
5. Add an optional localhost-backed browser replay check for macOS validation, default it to a few sentinel smoke pages, and keep a full sweep available as an explicit opt-in.
   - This gives the repo a browser-grade verification layer for figure/reference hydration without forcing every local run through a whole-book WebKit crawl, while still keeping the checker aligned with real page behavior.
   - Alternative considered: keep probing built pages through `file://` only, or override `requestAnimationFrame` inside the checker. Rejected because file-origin loading can suppress or delay the same-origin sidebar and metadata flows that the hosted site relies on, and scheduler overrides can hide the very timing bugs the replay should detect.
6. Delay `readerRuntimeInitialized` until the core boot sequence completes, allow one safe retry on synchronous initialization failure, and throttle/disconnect the sidebar observer once projected navigation stabilizes.
   - This prevents half-initialized pages from getting stuck in a permanently “done” state and stops sidebar mutations from repeatedly re-running the most expensive runtime hydration steps.
   - Alternative considered: keep the eager initialization flag and a long-lived whole-sidebar observer. Rejected because partial failures would remain unrecoverable and steady-state DOM churn would keep paying unnecessary runtime cost.

## Risks / Trade-offs

- [Risk] Build-time body-class stamping could drift from the preserve-outline-rail expectations for generated pages.
  → Mitigation: keep the page-variant table in one shared script module and assert the generated page body classes in site validation.
- [Risk] The runtime outline simulation could drift from browser behavior.
  → Mitigation: keep the check narrowly aligned to the same signals the reader uses today: headings, figures, tables, formulas, and immediate top-level block adjacency for figure fallback.
- [Risk] Alt-based figure fallback could misclassify ordinary paragraphs after images.
  → Mitigation: require a `Figure N`-style image alt and a short adjacent paragraph that does not read like body prose.
- [Risk] The browser-grade checker could become flaky or too environment-specific.
  → Mitigation: run it only when macOS `swift`/WebKit are available, serve `public/` through localhost instead of `file://`, expose a repo-owned hydration-ready signal from `theme/custom.js`, default to sentinel smoke pages while keeping a full sweep opt-in, and source preserve-outline expectations from the shared page-variant module rather than duplicating them in Swift.
- [Risk] Reader runtime boot could fail after partial DOM work, or sidebar mutations could trigger redundant full refreshes.
  → Mitigation: only mark runtime initialization complete after the core boot sequence succeeds, allow one bounded retry for synchronous boot failures, and disconnect the throttled sidebar observer once the projected navigation is stable.
