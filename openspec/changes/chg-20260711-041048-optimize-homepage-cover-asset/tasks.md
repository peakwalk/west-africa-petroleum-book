## 1. OpenSpec and failing regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for the homepage cover-asset optimization change.
- [x] 1.2 Add failing homepage regression checks for the optimized cover asset path, loading hints, and size contract.

## 2. Homepage cover implementation

- [x] 2.1 Generate the repo-owned optimized WebP cover asset from the existing PNG source at homepage-appropriate dimensions.
- [x] 2.2 Update the shared homepage generator so the current-edition cover card references the WebP asset with lazy loading and async decoding.
- [x] 2.3 Refresh built-site assertions so homepage output fails if it falls back to the heavy PNG cover asset.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted homepage generation tests through a red-green cycle for the new cover-delivery contract.
- [x] 3.2 Rebuild the site, run the landing-page verification command, and validate the OpenSpec change artifacts.
