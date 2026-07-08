## Context

The repo now contains a dedicated stakeholder icon rebuild script, a compare preview package under `artifacts/stakeholder_icons_trace_rebuild/`, and a baseline acceptance checker. That baseline is useful, but it has exposed a second problem: a package can pass screenshot-fidelity automation while still looking visibly less refined than the original design reference.

This means the change now has two quality targets rather than one:

- `baseline` trace fidelity: close enough to the screenshot to compare and filter candidates safely.
- `production` polish: clean enough to ship as a polished icon set without obvious trace-derived heaviness, wobble, or generic-library drift.

## Goals / Non-Goals

**Goals:**
- Produce a trace-rebuilt stakeholder icon package that passes the acceptance criteria as a complete set.
- Generate multiple candidate variants for each failing icon rather than forcing all icons through one rebuild method.
- Preserve the screenshot source as the visual truth for silhouette and negative space.
- Make the final SVGs frontend-usable and the PNG exports stable across all required sizes.

**Non-Goals:**
- Reopen unrelated homepage layout or CSS work.
- Treat a single automatic trace output as sufficient final output.
- Force every icon into one uniform reconstruction method when different icons need different approaches.
- Archive the change before the final package passes the acceptance checks.

## Decisions

### Decision: Use per-icon multi-variant generation
Each failing icon will generate at least two candidates. Candidate families may include screenshot-derived trace, proxy-vector cleanup, and hand-authored SVG reconstruction. The final selected icon is whichever candidate best survives both quantified comparison and manual review.

Alternative considered:
- Keep one global pipeline for all six icons. Rejected because the current failures show that some icons need direct screenshot reconstruction while others are better served by cleaned proxy geometry.

### Decision: Keep screenshot silhouette as the final truth source
Even when proxy vectors are used as a starting point, acceptance will still be measured against the screenshot-derived source reference. Proxy vectors are only scaffolding, not truth.

Alternative considered:
- Promote existing repo proxy vectors to the truth source for selected icons. Rejected because that would allow drift away from the supplied screenshot.

### Decision: Add explicit acceptance automation
The rebuild flow will include a dedicated acceptance checker. It will verify package completeness, SVG semantics, special-case constraints such as `oil_drop` negative space, and a quantified silhouette comparison baseline that can reject obviously wrong candidates before manual review.

Alternative considered:
- Rely on preview images and manual review only. Rejected because the user has asked for a repeatable rebuild-review loop, not a one-off visual judgement.

### Decision: Split acceptance into baseline and production profiles
The checker and the written criteria will distinguish between a `baseline` profile and a `production` profile. `Baseline` keeps the current role of candidate filtering and source-fidelity verification. `Production` adds stricter SVG semantics, path-economy heuristics, and a manual polish gate for the final delivery set.

Alternative considered:
- Keep a single acceptance profile and just tighten the current thresholds. Rejected because overlap-driven automation and polish-driven review are solving different problems and should not be collapsed into one number.

### Decision: Prefer manual cleanup over raw trace output
Automatic tracing is allowed only as a draft generator. Any candidate that still looks like direct raster tracing at final export quality must be rejected, even if it scores well enough on coarse overlap metrics.

Alternative considered:
- Accept high-overlap rough traces as long as they are close to the screenshot. Rejected because the acceptance criteria require production-ready smooth vector delivery, not only approximate shape overlap.

## Risks / Trade-offs

- [Quantified shape comparison can reward noisy traces that overlap well] -> Keep it in `baseline`, but add a separate `production` gate rather than pretending the same metrics can measure polish.
- [Manual SVG reconstruction can drift into redesign] -> Keep screenshot-derived source references visible in every compare preview and reject candidates that normalize into library-style symbols.
- [Different candidate pipelines per icon increase script complexity] -> Keep variant definitions explicit and per-icon rather than overgeneralizing the generator.
- [The worktree already has unrelated user changes] -> Limit edits to the stakeholder rebuild scripts, focused tests, and the OpenSpec files for this change.

## Migration Plan

1. Update the OpenSpec artifacts to describe the iterative multi-variant rebuild strategy.
2. Add failing acceptance automation for the current package.
3. Extend the rebuild script to emit multiple candidate variants per failing icon.
4. Generate compare previews and quantified scores, then select the best candidate per icon.
5. Refine failing icons and rerun acceptance until the full set passes.

## Open Questions

- None. The user has explicitly requested iterative rebuild, multi-scheme comparison, and repeated self-acceptance until pass.
