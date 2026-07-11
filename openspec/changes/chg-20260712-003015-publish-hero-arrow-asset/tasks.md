## 1. Asset delivery

- [x] 1.1 Add the existing hero-arrow SVG to the English-only public asset manifest.

## 2. Regression coverage

- [x] 2.1 Update site-render assertions to require the English asset and retain its French absence.

## 3. Verification

- [x] 3.1 Build the site and confirm the generated English asset exists at the CSS-referenced path.
- [x] 3.2 Run the complete site-render validation.
- [x] 3.3 Load the English homepage in a local browser and confirm the hero arrow returns HTTP 200 without a console 404.
