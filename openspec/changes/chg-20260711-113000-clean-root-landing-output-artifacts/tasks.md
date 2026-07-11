## 1. Cleanup contract

- [x] 1.1 Add OpenSpec proposal, design, tasks, and Chinese companion files for root landing output cleanup.
- [x] 1.2 Remove tracked root landing output files and add regression checks that keep them absent.

## 2. Generator default alignment

- [x] 2.1 Change standalone landing generation defaults to `public/`.
- [x] 2.2 Update `package.json` aliases and site-render assertions to reflect the public-scoped output contract.

## 3. Verification

- [x] 3.1 Run the targeted landing regression tests.
- [x] 3.2 Rebuild the site, run `test:site`, and validate the OpenSpec change.
