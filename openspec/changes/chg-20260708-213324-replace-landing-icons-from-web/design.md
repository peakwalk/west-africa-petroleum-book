## Context

The current landing implementation already separates icon surfaces by section: hero stats use `assets/icons/homepage/hero-*.svg`, stakeholder cards use `assets/icons/stakeholders/`, search-scope chips use `assets/icons/search-scope/`, and English topic-reference cards use `assets/icons/topics/`. The supplied 26-file pack maps cleanly onto those four groups: 6 hero icons, 6 stakeholder icons, 8 search-scope icons, and 6 topic icons.

This change is intentionally narrow. It does not revisit the landing-page information architecture, text, or layout system. The work is limited to replacing those 26 mapped asset files, keeping topic cards on SVG references, and updating verification to match the supplied files.

## Goals / Non-Goals

**Goals:**
- Replace the mapped 26 landing-page icon slots with the supplied SVG pack.
- Keep the existing asset paths stable where possible so markup churn stays small.
- Switch English topic-reference cards from PNG references to SVG references.
- Keep English and French generated landing pages building through the current site pipeline.
- Extend verification so the generated English homepage no longer depends on PNG topic-card icon paths.

**Non-Goals:**
- Redesign copy or section order.
- Introduce a new icon component system or inline all external SVGs into the page templates.
- Regenerate or remove unused legacy PNG assets that are no longer part of the rendered landing pages.
- Replace landing-page icon slots that are not covered by the supplied 26-file mapping.

## Decisions

### Decision: Use the supplied 26-file pack as the icon source of truth
The user-provided icon pack will be copied directly into the existing asset locations. This keeps the implementation aligned with the supplied art direction and avoids continuing to guess at icon metaphors or style with third-party libraries.

Alternative considered:
- Keep the current third-party substitutions. Rejected because the user explicitly wants the supplied pack used instead.

### Decision: Preserve existing asset filenames and section wiring
The change will overwrite existing asset files in place instead of renaming every reference. This minimizes template churn and lets the current site copy step keep working without new routing logic.

Alternative considered:
- Introduce new filenames and update every reference. Rejected because it adds noise without user-visible benefit.

### Decision: Move topic-reference cards from PNG to SVG at the helper layer
`scripts/shared/homepage-topic-reference.mjs` will emit `.svg` topic icon URLs so the English homepage actually uses the new vector assets.

Alternative considered:
- Keep using PNGs and only refresh the underlying SVG siblings. Rejected because the page would still render the legacy raster topic icons.

### Decision: Limit substitution strictly to the mapped 26 assets
The supplied pack does not cover the French compatibility feature, audience, or country-signal icons, and it does not cover the adaptive control sprite icons. Those non-mapped surfaces will remain untouched in this change.

Alternative considered:
- Force-fit the supplied pack onto additional icon slots. Rejected because the file names and count only clearly map to 26 surfaces.

## Risks / Trade-offs

- [The supplied custom icons may not match the temporary Heroicons-tuned scale] -> Restore the pre-library sizing for stakeholder, search-scope, and topic icon groups so the provided artwork uses the intended visual weight.
- [The supplied pack covers only a subset of landing-page icons] -> Restrict replacement to the exact mapped 26 surfaces and leave other icon slots unchanged.
- [Topic icon contract changes from PNG to SVG] -> Update both source and generated-page assertions in `scripts/test-site-render.sh`.
