## 1. OpenSpec and failing regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for the cropped-icon PNG cleanup change.
- [x] 1.2 Add failing regression checks that require the cropped-icon PNG variants to stay absent from source and built asset trees.

## 2. Source cleanup and documentation

- [x] 2.1 Update the cropped-icon README files to reflect the WebP production-asset contract.
- [x] 2.2 Delete the unused PNG icon copies from `assets/icons/homepage-cropped/`.
- [x] 2.3 Refresh built-site assertions so the copied public asset trees also fail if those PNG files return.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted landing tests through a red-green cycle for the cropped-icon PNG absence contract.
- [x] 3.2 Rebuild the site, run landing-page verification, and validate the OpenSpec change artifacts.
