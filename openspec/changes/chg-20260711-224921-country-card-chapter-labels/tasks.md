## 1. English country-card labels

- [x] 1.1 Add the published `3.1`–`3.16` chapter number to the corresponding English country metadata records.
- [x] 1.2 Render each English country-card analysis link as `Chapter <chapterNumber> →` while preserving the existing destination and French branch.

## 2. Regression coverage

- [x] 2.1 Extend the generated-homepage country-card test to assert the exact label and `href` for all 16 countries.
- [x] 2.2 Update the site-render assertion that currently expects the obsolete country-card label.

## 3. Verification

- [x] 3.1 Run the focused country-card regression test.
- [x] 3.2 Run the complete site-render validation.
- [x] 3.3 Inspect the generated English cards at desktop, tablet, and mobile widths; confirm labels, destinations, and unchanged interaction styling.
