## Why

Petroleum discovery totals use inconsistent definitions across governments, operators, and publications, so the country-card figures are difficult to verify and can undermine the homepage's authority. The homepage should present only country-summary metrics that are objective and stable enough to defend.

## What Changes

- Remove the discovery-count data, label, and rendered metric row from all 16 homepage country cards.
- Retain each card's producing-field count and all other country identity, status, hydrocarbon, and navigation information.
- Rebalance the country-card vertical layout while preserving equal-height cards and responsive grid behavior.
- Add generated-page regression checks that prevent discovery counts from being reintroduced into country cards.

## Capabilities

### New Capabilities

- `homepage-country-card-metrics`: Defines the objective metric content and presentation invariants for homepage country cards.

### Modified Capabilities

- None.

## Impact

- Homepage content source and country-card renderer: `scripts/shared/homepage-content.mjs`.
- Homepage country-card layout: `assets/css/landing.components.css`.
- Generated-site regression assertions: `scripts/test-site-render.sh` and a focused country-card test if needed.
- Generated landing output only; no direct edits to `public/`, no new dependencies, API changes, or book-content changes.
