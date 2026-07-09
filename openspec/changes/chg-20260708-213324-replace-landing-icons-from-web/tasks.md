## 1. OpenSpec and source-of-truth updates

- [x] 1.1 Write the proposal, design, spec, and Chinese companion files for the landing icon asset replacement change.

## 2. Landing icon implementation

- [x] 2.1 Replace the non-hero-stat landing icon assets with curated web-sourced SVG files while keeping the current asset paths stable.
- [x] 2.2 Update the homepage topic-reference helper to emit SVG icon paths instead of PNG icon paths.
- [x] 2.3 Normalize French compatibility homepage icon dimensions so the new SVG assets render without distortion.
- [x] 2.4 Refresh the landing sprite controls from the same icon source while preserving `currentColor` behavior.

## 3. Verification

- [x] 3.1 Update site-render assertions for the new topic SVG contract and any related asset existence checks.
- [x] 3.2 Rebuild the site and run the narrowest useful landing-page verification commands.
