## Context

The English landing page is generated from `scripts/shared/homepage-content.mjs`. A single `COUNTRIES` array currently stores both the producing-field and discovery-count values for 16 countries, and `renderCountryCard` turns each value into a row in `.country-metrics`. The shared country-card component reserves a common minimum height and places the country-analysis link at the bottom of each card. The generated English homepage is the affected user surface; the French homepage uses a compatibility rendering path and does not render these country cards.

The source-of-truth requirement is narrow: remove a subjective statistic from country cards while preserving the objective producing-field count and all unrelated homepage discovery references.

## Goals / Non-Goals

**Goals:**

- Render exactly one objective metric, producing fields, in each of the 16 country cards.
- Remove obsolete discovery-count data from the country-card source model so it cannot be accidentally rendered later.
- Keep cards visually balanced, equal-height, accessible, and usable at desktop, tablet, and mobile breakpoints.
- Prove the generated HTML does not contain a discovery metric within any country card.

**Non-Goals:**

- Do not alter discovery references in the hero, footer, search taxonomy, map, book chapters, or other pages.
- Do not redefine or research country production-field counts.
- Do not redesign the country-card information architecture, navigation, status badges, flags, or responsive grid.

## Decisions

### Make the data model and template agree

Delete the `discoveries` property from every country item, remove the localized discovery label, and remove the second metric row from `renderCountryCard`.

This removes the metric at its source rather than merely hiding it with CSS. It prevents stale, subjective data from surviving in generated HTML or being reused by future card variants.

Alternative considered: hide the discovery row with CSS. Rejected because the content would remain in the DOM, be visible to assistive technology and search indexing, and could reappear in a future style change.

### Preserve the existing metric semantics and card structure

Keep the `dl`/`dt`/`dd` metric structure with a single producing-field entry. Preserve the article, heading, status, hydrocarbon list, and country-analysis link unchanged.

This is the smallest semantic change, avoids breaking existing class hooks, and keeps the card understandable to screen readers.

Alternative considered: replace the definition list with free-form text. Rejected because it is unnecessary markup churn and weakens the existing metric relationship.

### Rebalance with one shared card-height rule

Adjust the common `.country-card-v2` minimum height and only the vertical spacing needed after the row is removed. Retain the bottom-aligned analysis link and existing responsive grid rules.

One shared rule keeps the 16 cards visually uniform without country-specific exceptions. The final value will be chosen from generated-page checks at desktop, tablet, and mobile widths rather than guessed from the removed row alone.

Alternative considered: add per-status or per-country height overrides. Rejected because it creates fragile exceptions and violates the equal-card requirement.

### Test rendered behavior instead of source-string absence alone

Add focused generated-homepage assertions that count 16 country cards, require one producing-field metric per card, and reject English or French discovery labels within the card fragments. Keep the existing full site-render test as the integration gate.

This checks what visitors receive and guards both the data and rendering layers.

Alternative considered: only check that `discoveries:` no longer exists in the source file. Rejected because it cannot detect a template regression or an equivalent reintroduced rendering path.

## Risks / Trade-offs

- [A reduced fixed height can make a long country label or status crowd the bottom link] → Use the existing flexible grid layout, test every status category, and tune one shared minimum height at all target widths.
- [A broad text search could remove unrelated discovery content] → Limit edits and assertions to `COUNTRIES`, `renderCountryCard`, card CSS, and card fragments in generated homepage HTML.
- [A brittle visual assertion can overfit CSS values] → Assert semantic output and layout invariants; use rendered screenshots only to choose and confirm the spacing rather than lock arbitrary pixel values into tests.

## Migration Plan

1. Create and validate the OpenSpec artifacts.
2. Update the country-card source model and rendering template.
3. Tune the shared card layout and add targeted rendered-page regression checks.
4. Run focused tests, the landing-site build/render suite, and desktop/tablet/mobile visual checks.
5. Publish through the normal generated-site build; no data migration is required.

Rollback is a small source revert: restore the deleted data fields and metric row, then restore the prior shared card-height value. No persisted data, API consumer, or generated artifact requires a separate rollback.

## Open Questions

- None. The ticket explicitly scopes the removal to country cards and requires equal-height responsive cards.
