## 1. OpenSpec scope and styling baseline

- [x] 1.1 Write the proposal, design, spec, and Chinese companion files for the homepage text-color consistency change.
- [x] 1.2 Identify the current homepage white-surface text roles and map them to a smaller shared token set before touching module styles.

## 2. Homepage text-role consolidation

- [x] 2.1 Add or normalize shared homepage text-color tokens in `assets/css/landing.base.css` for headings, supporting body copy, metadata, and interactive text.
- [x] 2.2 Update white-surface homepage modules to use those shared roles, including navigation, stakeholder cards, country cards, search chips, topic cards, and summary cards, while preserving current layout and copy.
- [x] 2.3 Review responsive homepage overrides and clear any leftover hard-coded text blues that would break the same hierarchy on tablet or mobile.

## 3. Verification

- [x] 3.1 Run the narrowest relevant homepage styling verification and confirm that no layout, route, or copy regressions were introduced.
- [x] 3.2 Review the final homepage text hierarchy against the approved composition goals, confirming that descriptive text is calmer than interactive text and that links share one consistent visual family.
