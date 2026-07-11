## 1. Country-card source and rendering

- [x] 1.1 Remove all 16 `discoveries` values and the localized discovery label from the country-card source model.
- [x] 1.2 Render only the producing-field metric while preserving every other country-card element and link.

## 2. Layout and regression coverage

- [x] 2.1 Rebalance the shared country-card minimum height and vertical spacing without adding country-specific overrides.
- [x] 2.2 Add generated-page assertions for 16 cards, one producing-field metric per card, no card-level discovery metric, and preservation of unrelated discovery content.

## 3. Validation

- [x] 3.1 Run the focused generated-homepage regression test and the landing-site render suite.
- [x] 3.2 Inspect desktop, tablet, and mobile renders for balanced, equal-height, unclipped country cards.
- [x] 3.3 Validate the OpenSpec change and record completed tasks.
