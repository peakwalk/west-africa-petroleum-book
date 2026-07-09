## Context

The homepage map overview is generated from `scripts/shared/homepage-content.mjs` and styled in `assets/css/landing.discovery.css`. The current implementation already moved away from the old abstract polygon, but it still uses a repo-cropped panel plus a separate Cabo Verde inset, so the clickable hotspots drift from the exact flag positions in the user-supplied reference SVG.

This task is intentionally narrow. The goal is not to redesign the whole homepage again; it is to make the existing map-overview module visually line up with the supplied target while keeping the current routing model intact. The country card grid remains the primary entry path. The map panel remains secondary, but it must now look like the approved west Africa west-coast composition.

That same primary entry path currently renders flags through an external SVG sprite URL. While Chromium loads that pattern, some standalone/static renderers do not resolve external `<use>` references consistently. Because the country card grid remains the main homepage navigation surface, the flag markup needs a repo-local compatibility fix as part of this change.

## Goals / Non-Goals

**Goals:**
- Match the approved map-overview composition closely on desktop, including copy density, blue CTA treatment, and the exact user-supplied west-coast political SVG with its embedded flag layout.
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

### Decision: Use the user-supplied SVG as the single visual baseline
The implementation will use the user-supplied `africa_map_accurate.svg` directly as the visual baseline for the right-hand map panel. This removes the extra crop and inset coordinate system, which is the main reason the current hotspots no longer line up exactly with the visible flags.

Alternative considered:
- Rebuild the map as pure CSS/SVG immediately. Rejected for this change because it is slower, higher-risk, and less likely to match the approved composition precisely on the first pass.

### Decision: Preserve routing by aligning hotspots directly to the flags embedded in the SVG
The visible map panel will keep the flags drawn inside the supplied SVG and place the clickable hotspots directly over those flag bounds, including the Cabo Verde inset already present in the artwork. This keeps the destinations aligned with homepage card links while collapsing the map interaction to a single coordinate system.

Alternative considered:
- Keep the cropped mainland panel plus a separate Cabo Verde inset. Rejected because it preserves the current alignment problem and forces every hotspot change through two different layout transforms.

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
- [SVG transparency can reveal more ocean around the west-coast composition than the cropped panel did] -> Keep the existing light blue canvas background behind the vector so the surrounding negative space still reads as intentional map framing.
- [Flag-sized hotspots can become harder to hit on smaller screens] -> Keep minimum hotspot dimensions in CSS so touch targets remain usable even when the visible flag art scales down.
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
