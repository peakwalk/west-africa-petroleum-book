## 1. OpenSpec and regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for selective public asset copying.
- [x] 1.2 Add failing site-render assertions for source-only public images and French-tree English-homepage assets that should no longer be copied.

## 2. Build asset publication changes

- [x] 2.1 Replace full-tree public asset copying in `scripts/build_site.mjs` with shared and English-only asset manifests.
- [x] 2.2 Keep current landing and book runtime references intact while omitting source-only image backups from both public trees.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted regression checks through a red-green cycle for the new omission contract.
- [x] 3.2 Rebuild the site, run `test:site`, and validate the OpenSpec change artifacts.
