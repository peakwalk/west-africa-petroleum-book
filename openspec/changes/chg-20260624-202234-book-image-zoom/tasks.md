## 1. OpenSpec and source-level checks

- [x] 1.1 Update the proposal, design, and `book-reader-image-zoom` capability spec to describe browser-native new-tab image opening for body figures.
- [x] 1.2 Replace the theme and site-render assertions so they cover the new-tab contract and the removal of the vendored dependency.

## 2. Dependency rollback

- [x] 2.1 Remove the vendored pan/zoom helper from theme loading in both edition `book.toml` files.
- [x] 2.2 Remove the checked-in pan/zoom vendor files and source notes.

## 3. Reader image-open implementation

- [x] 3.1 Replace the custom body-figure viewer in `theme/custom.js` with a lightweight new-tab image opener.
- [x] 3.2 Keep eligible figure images keyboard-focusable and support click plus `Enter`/`Space` activation.
- [x] 3.3 Keep the behavior scoped to `.reader-article .figure-card img` and open only the activated image in multi-image figures.
- [x] 3.4 Remove obsolete overlay-viewer styles from `theme/custom.css` while preserving keyboard focus affordance.

## 4. Verification

- [x] 4.1 Run the targeted Python theme tests for `theme/custom.js` and `theme/custom.css`.
- [x] 4.2 Run `sh scripts/test-site-render.sh`.
- [x] 4.3 Run the narrowest useful site build/test command needed to confirm the reader output still renders cleanly.
