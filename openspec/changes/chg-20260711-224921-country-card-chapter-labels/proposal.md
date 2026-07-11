## Why

The English homepage currently labels every country-card link as “Country Analysis”, which hides the card's location in the book. UA-14 requires the homepage to present Upstream Atlas as a reference book by showing the published English chapter number for each country without changing navigation.

## What Changes

- Replace the English country-card link label with its corresponding `Chapter 3.X →` label for all 16 countries.
- Preserve the existing chapter paths, anchors, card markup, styling, hover behaviour, and responsive layout.
- Add generated-homepage regression coverage for every country-card label and destination.
- Keep the French compatibility homepage unchanged because it does not render the English set of 16 country cards and uses a different chapter structure.

## Capabilities

### New Capabilities

- `homepage-country-card-chapter-labels`: Render and validate published English chapter-number labels on homepage country-card links.

### Modified Capabilities

None.

## Impact

- Affected source: `scripts/shared/homepage-content.mjs`.
- Affected checks: `tests/test_homepage_country_cards.py` and `scripts/test-site-render.sh`.
- No URL, API, dependency, chapter-content, figure, or French-edition changes.
