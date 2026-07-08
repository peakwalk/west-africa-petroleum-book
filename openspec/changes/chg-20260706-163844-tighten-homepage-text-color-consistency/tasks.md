## 1. OpenSpec scope and styling baseline

- [x] 1.1 Write the proposal, design, spec, and Chinese companion files for the homepage text-color consistency change.
- [x] 1.2 Identify the current homepage white-surface text roles and map them to a smaller shared token set before touching module styles.

## 2. Homepage text-role consolidation

- [x] 2.1 Add or normalize shared homepage text-color tokens in `assets/css/landing.base.css` for headings, supporting body copy, metadata, and interactive text.
- [x] 2.2 Update white-surface homepage modules to use those shared roles, including navigation, stakeholder cards, country cards, search chips, topic cards, and summary cards, while preserving current layout and copy.
- [x] 2.3 Review responsive homepage overrides and clear any leftover hard-coded text blues that would break the same hierarchy on tablet or mobile.
- [x] 2.4 Re-promote content-bearing sublabels and empty-state lines from the metadata role to the supporting body role wherever the approved screenshot comparison shows the current result is too quiet.
- [x] 2.5 Strengthen shared CTA and control affordances for white-surface links, stakeholder cards, and search chips through typography and border/shadow treatment without changing layout or copy.
- [x] 2.6 Apply a final density pass to country cards, topic cards, and summary cards so the remaining white-surface modules match the approved screenshot more closely without reopening the broader homepage hierarchy.
- [x] 2.7 Replace the six hero-stat SVG assets in place with the user-supplied V10 source set while keeping the existing hero metric markup and CSS hooks unchanged.
- [x] 2.8 Replace the six topic-card inline icons with the user-supplied current approved SVG asset set while keeping the existing topic card layout and class hooks unchanged.

## 3. Verification

- [x] 3.1 Run the narrowest relevant homepage styling verification and confirm that no layout, route, or copy regressions were introduced.
- [x] 3.2 Review the final homepage text hierarchy against the approved composition goals, confirming that descriptive text is calmer than interactive text and that links share one consistent visual family.
- [x] 3.3 Re-check the approved screenshot comparison and confirm that the white-surface sections no longer feel lighter or sparser than the reference because of under-emphasized body text or CTAs.
