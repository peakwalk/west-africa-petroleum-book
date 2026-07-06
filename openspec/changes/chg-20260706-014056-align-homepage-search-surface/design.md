## Context

The homepage search section is generated from `scripts/shared/homepage-content.mjs` and styled in the landing CSS split introduced earlier. The current section already has the correct destination routing, but its presentation differs from the supplied reference in two visible ways: duplicated title treatment and a detached submit button.

The English homepage `Browse by Topic` section is also generated from the same source file, and it still reflects the earlier information-architecture draft with a large narrative heading and ten topical cards. The approved reference instead shows one compact section title plus six icon-led cards.

The closing summary-modules row is similarly still on an older layout: four equal-width cards, uppercase kicker styling, plain bullet lists, and no visible action links. The supplied reference instead uses mixed card widths, title-case card headings, green checkmark bullets, and explicit calls to action at the bottom of three cards.

This change is intentionally narrow. It should not redesign the broader homepage information architecture again. The work is limited to making the search title/field composition, the English `Browse by Topic` section, and the English summary-modules row visually align with the approved references while keeping the current localization, routing, and query-string behavior.

## Goals / Non-Goals

**Goals:**
- Match the supplied reference for the homepage search title and search-field composition as closely as practical in the existing landing system.
- Match the supplied reference for the English homepage `Browse by Topic` heading and six-card composition as closely as practical in the existing landing system.
- Match the supplied reference for the English homepage summary-modules row, including card proportions, heading treatment, list markers, and visible CTA links.
- Keep the existing `search` query parameter contract and book destination unchanged.
- Keep the existing chapter destinations behind the topic cards unchanged.
- Keep the summary-card destinations internal to already-existing homepage or chapter-library routes.
- Preserve localized copy and the search-scope chip links below the field.
- Keep the French compatibility homepage on its current topic-card fallback layout.
- Keep the change limited to homepage source templates, section-local CSS, and targeted verification.
- Maintain usable responsive behavior on tablet and mobile widths.

**Non-Goals:**
- Redesign the chips below the search field.
- Change the underlying search experience inside the book reader.
- Introduce a JavaScript-powered autocomplete or a new search backend.
- Rebuild the French compatibility topic section to match the English design reference.
- Introduce a new release-notes or roadmap backend just to support the summary cards.
- Restyle unrelated homepage sections.

## Decisions

### Decision: Keep homepage generator markup as the source of truth
The new search-section structure will be implemented in `scripts/shared/homepage-content.mjs` and propagated through the existing site build. Generated `index.html` variants will be rebuilt instead of patched by hand.

Alternative considered:
- Patch generated homepage files directly. Rejected because it would drift from the generator and be overwritten on the next build.

### Decision: Replace the detached submit button with an integrated search shell
The form will render a single rounded field shell containing a leading submit control/icon and the search input. This most closely matches the reference while preserving native form submission through click or Enter.

Alternative considered:
- Keep the current right-side CTA button and only restyle it. Rejected because the provided reference does not show a detached search CTA, so the overall layout would still look wrong.

### Decision: Show one visible heading in the section while retaining accessibility labeling
The section will stop rendering the eyebrow as visible text and rely on the centered `h2` as the only visible title. The form will keep a screen-reader label so accessibility does not depend on placeholder text.

Alternative considered:
- Keep both the eyebrow and title and try to tighten spacing. Rejected because the duplicate visible heading is itself one of the mismatches against the approved design.

### Decision: Scope styling changes to the search section and responsive overrides
The layout, spacing, icon alignment, and pill-field treatment will be handled with search-section selectors in `assets/css/landing.discovery.css`, with only the smallest responsive adjustments in tablet/mobile CSS files.

Alternative considered:
- Change shared heading or button tokens globally. Rejected because it would risk unrelated homepage regressions outside this section.

### Decision: Use a section-local inline SVG icon set for the search-scope chips
The search-scope chips will render their own inline SVG icons instead of mixing existing hero and homepage sprite assets. The current asset set uses inconsistent metaphors, stroke styles, and accent colors, so reusing it would still drift from the approved reference even after CSS tuning.

Alternative considered:
- Reuse the existing homepage sprite and hero SVG assets. Rejected because the mixed gold-accent artwork does not visually match the blue, single-tone chip icons in the approved design.

### Decision: Replace the English browse-by-topic editorial layout with a six-card reference strip
The English homepage topic section will stop rendering the large narrative `h2` plus ten-card grid. Instead it will render one visible section heading, six topic cards in the approved order, and shorter descriptions that fit the compact card design.

Alternative considered:
- Keep the ten-card information architecture and only tighten spacing. Rejected because the supplied design changes the section structure itself, not just the spacing.

### Decision: Keep the topic-card redesign scoped to the English homepage variant
The new six-card layout will be used only by the English homepage generator. The French compatibility homepage will continue to render its current compact fallback cards until a dedicated French reference exists.

Alternative considered:
- Apply the new English topic-card design to both locales immediately. Rejected because the French compatibility homepage is intentionally simplified and does not currently have the same content set or approved reference.

### Decision: Use a dedicated inline SVG icon set for the six topic cards
The topic cards will render their own inline SVG icons for value chain, fiscal regimes, national oil companies, upstream operations, governance, and country analysis. This keeps the iconography visually consistent with the supplied reference without depending on the mixed legacy homepage sprite artwork.

Alternative considered:
- Reuse the existing homepage sprite and chapter icons. Rejected because the available assets do not provide the required metaphors in a consistent blue, outlined style.

### Decision: Retain the existing summary content but restyle it into the approved four-card composition
The summary-modules row will keep the existing English content set: latest updates, current edition, topics covered, and future development. The redesign will be structural and presentational rather than editorial, with three visible action links added to cards that already summarize broader destinations.

Alternative considered:
- Replace the summary content with new card bodies to mirror the design word-for-word. Rejected because the current copy already covers the intended surfaces, and the user asked for visual alignment rather than a broader content rewrite.

### Decision: Use existing internal destinations for new summary-card CTAs
The new summary action links will point to existing internal destinations rather than inventing new pages. `View all updates` and `Learn more` will link to the chapter library, while `View all topics` will link back to the homepage topics section.

Alternative considered:
- Add placeholder or dead-end links pending a future updates page. Rejected because visible CTAs should remain functional even in a narrowly scoped visual refresh.

### Decision: Split summary heading styling from topic kicker styling
`summary-card-eyebrow` will stop sharing the uppercase accent treatment used by topic kickers. The summary card headings need their own darker, title-case typography to match the supplied reference.

Alternative considered:
- Keep one shared kicker style and only change card spacing. Rejected because the shared uppercase styling is one of the clearest mismatches against the design reference.

## Risks / Trade-offs

- [Localized placeholder strings have different lengths] -> Keep the input flexible and avoid a fixed-width button inside the field so French text still fits.
- [Removing the detached CTA changes the obvious click target] -> Make the leading icon/button focusable and preserve standard Enter-to-submit behavior.
- [Section-local CSS could drift at smaller breakpoints] -> Add explicit narrow-width overrides and verify rebuilt English and French homepage outputs.
- [Six cards at desktop width reduce card width compared with the previous five-column grid] -> Shorten the card copy, keep card typography compact, and let tablet/mobile fall back to fewer columns through existing responsive overrides.
- [A new English-only topic layout could accidentally affect the French compatibility cards] -> Gate the new styling behind topic-reference modifier classes and add a French homepage assertion that the reference-grid class is absent.
- [Adding visible CTAs could imply destinations that do not yet have dedicated pages] -> Reuse current internal chapter-library and homepage-anchor routes so every CTA remains functional.
- [Summary layout now depends on asymmetric desktop columns] -> Keep tablet/mobile breakpoints on the existing two-column/one-column fallbacks so the new proportions stay desktop-only.

## Migration Plan

1. Add the OpenSpec proposal, design, spec, and bilingual companion files for this search-surface alignment change.
2. Update homepage generator markup, section-local CSS, English topic-card helper data, and summary-card action markup.
3. Refresh generated homepage outputs through the normal site build.
4. Run targeted site verification for homepage markup/CSS expectations.
5. If the result is unacceptable, roll back by reverting the homepage search/topic/summary markup, helper data, and section-local CSS changes; no data migration is involved.

## Open Questions

- None for this change. The supplied reference is specific enough to keep the implementation scoped and deterministic.
