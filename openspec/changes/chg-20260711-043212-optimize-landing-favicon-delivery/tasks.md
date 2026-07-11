## 1. OpenSpec and failing regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for the landing favicon delivery change.
- [x] 1.2 Add failing landing-shell regression checks for the split favicon paths and asset-size contract.

## 2. Landing favicon implementation

- [x] 2.1 Generate the `32x32` favicon PNG and the dedicated Apple touch icon PNG from the existing source favicon.
- [x] 2.2 Update the shared landing head generator to reference the new split favicon assets.
- [x] 2.3 Refresh built-site assertions so landing output fails if it falls back to the oversized shared favicon path.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted landing generation tests through a red-green cycle for the split favicon contract.
- [x] 3.2 Rebuild the site, run landing verification, and validate the OpenSpec change artifacts.
