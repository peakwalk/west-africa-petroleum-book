## 1. OpenSpec and failing regression coverage

- [x] 1.1 Add the proposal, design, spec, and Chinese companion files for the landing unused-image cleanup change.
- [x] 1.2 Add failing regression checks that require the retired landing image assets to stay absent from source and built output trees.

## 2. Source asset cleanup

- [x] 2.1 Delete the retired landing image files from `assets/images/` without touching active landing source chains.
- [x] 2.2 Refresh built-site assertions so landing validation fails if those retired images reappear in generated assets.

## 3. Rebuild and verification

- [x] 3.1 Run the targeted landing tests through a red-green cycle for the retired asset absence contract.
- [x] 3.2 Rebuild the site, run landing-page verification, and validate the OpenSpec change artifacts.
