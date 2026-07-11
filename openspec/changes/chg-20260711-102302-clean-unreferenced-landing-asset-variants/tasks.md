## 1. OpenSpec and failing regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for the unreferenced landing-asset cleanup change.
- [x] 1.2 Add failing regression checks that require the unreferenced historical asset variants to stay absent from source and built asset trees.

## 2. Source asset cleanup

- [x] 2.1 Delete the unreferenced historical asset variants from `assets/images/` without touching the active graywhite book-theme chain.
- [x] 2.2 Refresh site-render assertions so the source tree and public asset trees fail if those variants return.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted landing tests through a red-green cycle for the unreferenced-asset absence contract.
- [x] 3.2 Rebuild the site, run landing-page verification, and validate the OpenSpec change artifacts.
