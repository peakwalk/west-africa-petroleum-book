## 1. OpenSpec and test contract

- [x] 1.1 Add the flash-stability proposal, design, and capability spec for the narrowed `v1` scope
- [x] 1.2 Update `scripts/test-site-render.sh` to assert the new static-sidebar and boot-stability contract before implementation
- [x] 1.3 Run `npm run test:site` and confirm the new assertions fail before implementation is complete

## 2. Static sidebar implementation

- [x] 2.1 Create `scripts/build_static_reader_sidebar.mjs` to parse `public/book/toc.html`, render final sidebar projection markup, and inject it into generated book pages
- [x] 2.2 Wire the new static-sidebar build step into `package.json` and `scripts/preview.sh`
- [x] 2.3 Update generated-page contracts so projected sidebar markup is present and active-row state is encoded in the HTML output

## 3. Runtime cleanup and stabilization

- [x] 3.1 Remove inline sidebar projection bootstrap logic from `theme/index.hbs`
- [x] 3.2 Remove runtime sidebar reprojection logic from `theme/custom.js` while keeping the existing internal scroller bridge unchanged
- [x] 3.3 Add boot-state layout transition gating and non-structural projected-sidebar scroll persistence

## 4. Verification

- [x] 4.1 Run `npm run test:site` until the full render assertions pass
- [x] 4.2 Run `sh scripts/test-preview-build.sh` to verify preview builds include the static sidebar step
- [x] 4.3 Manually smoke-test representative left-rail navigations and confirm the visible flash is gone without scroll-model regressions
