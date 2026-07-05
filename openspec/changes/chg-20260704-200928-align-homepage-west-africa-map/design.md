## Context

The homepage map overview is generated from `scripts/shared/homepage-content.mjs` and styled in `assets/css/landing.discovery.css`. The current implementation draws the map area with CSS gradients and clipped polygons, which made it fast to ship but does not resemble the approved west-coast political reference the user expects.

This task is intentionally narrow. The goal is not to redesign the whole homepage again; it is to make the existing map-overview module visually line up with the supplied target while keeping the current routing model intact. The country card grid remains the primary entry path. The map panel remains secondary, but it must now look like the approved west Africa west-coast composition.

That same primary entry path currently renders flags through an external SVG sprite URL. While Chromium loads that pattern, some standalone/static renderers do not resolve external `<use>` references consistently. Because the country card grid remains the main homepage navigation surface, the flag markup needs a repo-local compatibility fix as part of this change.

## Goals / Non-Goals

**Goals:**
- Match the approved map-overview composition closely on desktop, including copy density, blue CTA treatment, Cape Verde inset, and west-coast political basemap.
- Preserve the existing country-analysis deep links from the map surface.
- Keep country-card flags rendering reliably in standalone homepage output.
- Keep the change repo-local, static-build-friendly, and limited to homepage sources, assets, and verification.
- Maintain responsive behavior so the module still works on tablet and mobile layouts.
- Make homepage breakpoint behavior explicit and stable across four ranges: `0-767` phone, `768-1023` pad, `1024-1439` small desktop, and `1440+` desktop locked.

**Non-Goals:**
- Redesign the country cards, topic cards, hero, or other homepage sections.
- Introduce a new map framework, GIS dependency, or dynamic runtime.
- Add rich hover tooltips or a second layer of petroleum metadata in this change.
- Rebuild the map as a perfectly semantic vector geography if that would slow delivery of the approved visual match.

## Decisions

### Decision: Use a repo-owned reference-derived map panel image for the visual baseline
The implementation will use a repo-owned cropped map panel derived from the approved reference as the visual baseline for the right-hand map panel. This is the most direct way to achieve the requested pixel-level alignment without adding an external geographic data pipeline or hand-drawing a fragile SVG approximation under time pressure.

Alternative considered:
- Rebuild the map as pure CSS/SVG immediately. Rejected for this change because it is slower, higher-risk, and less likely to match the approved composition precisely on the first pass.

### Decision: Preserve routing with focusable hotspots layered over the reference panel
The visible map panel will no longer render live flag DOM for the panel itself. Instead, the existing country routing model will be preserved through transparent, focusable hotspots positioned over the visual flags in the reference panel. This keeps the country destinations aligned with homepage card links while allowing the artwork to stay locked to the approved reference.

Alternative considered:
- Render a second visible flag layer on top of the panel. Rejected because it would create visual drift from the approved reference and require a second round of manual optical alignment.

### Decision: Keep all copy and markup changes in the homepage generator, not in generated output
The revised title, descriptive copy, CTA markup, and map panel structure will live in `scripts/shared/homepage-content.mjs`, with `index.html` and `public/` regenerated from source. This follows the repo rule that generated landing outputs should not be hand-maintained.

Alternative considered:
- Patch `index.html` directly. Rejected because it would drift from the source generator and break the next rebuild.

### Decision: Inline the shared country-flag sprite once in homepage HTML
The homepage generator will embed the shared country-flag sprite definitions directly in the page and point country-card `<use>` elements at local fragment IDs such as `#nigeria`. This preserves the existing visual system while removing the dependency on external sprite resolution for the homepage's primary card grid.

Alternative considered:
- Keep `/assets/icons/country-flags.svg#...` references. Rejected because external SVG symbol resolution is inconsistent in some standalone/static preview environments, which makes the country cards look broken even though the routes still work.

### Decision: Add a section-local CTA treatment instead of changing the global primary button token
The approved reference uses a blue CTA inside this module, while the broader homepage currently uses the orange primary button token. The implementation will apply a local blue CTA treatment to the map-overview module instead of changing the global primary button style for the whole landing page.

Alternative considered:
- Change `.button-primary` globally. Rejected because it would unintentionally restyle hero/search/footer CTAs outside this task's scope.

### Decision: Consolidate homepage responsive behavior around four named ranges
The homepage will treat `0-767` as phone, `768-1023` as pad, `1024-1439` as small desktop, and `1440+` as desktop locked. Existing homepage-specific breakpoints such as `700`, `900`, `1100`, `1200`, and `1201` will be retired or narrowed so the major layout shifts happen only at the agreed range boundaries.

On locked desktop, key homepage typography and spacing that currently continue to scale with viewport width will be frozen to stable values. This avoids cases where a wider desktop unexpectedly introduces extra line wraps or larger hero metrics while the layout columns stay effectively fixed.

Alternative considered:
- Keep the current fluid desktop typography and only patch the map title. Rejected because the user explicitly asked for a clearer phone/pad/desktop model, and the map title issue exposed a wider breakpoint consistency problem.

## Risks / Trade-offs

- [Reference-derived raster art can drift from future country sets or flag updates] -> Keep hotspot routing data separate from the image so the navigation contract remains editable even if the artwork is later replaced.
- [Raster scaling can soften on very large screens] -> Use a sufficiently large source asset, constrain the section width, and let the image scale proportionally rather than stretch.
- [Transparent hotspots are less self-evident than visible interactive markers] -> Add hover/focus outlines so mouse and keyboard users still get a clear affordance.
- [Inlining the sprite slightly increases homepage HTML size] -> Accept the small markup increase because the sprite is reused across all country cards and removes a more visible rendering failure.
- [The French homepage may share some landing CSS] -> Keep selectors scoped to the map-overview module and verify the generated localized outputs remain intact.
- [Breakpoint consolidation can shift other homepage modules unexpectedly] -> Limit the explicit range lock to homepage-facing selectors, keep micro phone tweaks only where needed, and verify the built homepage on representative widths.

## Migration Plan

1. Add the OpenSpec artifacts and reference asset for the homepage map alignment change.
2. Update homepage content generation and section-specific CSS in source files only.
3. Rebuild the homepage/site outputs so generated `index.html` and `public/` reflect the change.
4. Run targeted site verification and capture a local screenshot of the updated map-overview section for comparison against the approved reference.
5. If the result is not acceptable, roll back by reverting the new asset and the section-local template/CSS changes; no persistent data migration is involved.

## Open Questions

- None for this change. The implementation deliberately optimizes for a narrow, approved visual match without reopening the broader homepage architecture.
