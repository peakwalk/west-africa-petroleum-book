## 1. Shared Classification

- [x] 1.1 Add a shared page-variant module and stamp the resolved body classes into generated book pages during shell localization.
- [x] 1.2 Remove the runtime page-variant classifier and update source-level tests/assertions to cover build-time body-class injection instead.

## 2. Runtime Regression Guard

- [x] 2.1 Add a site-render validation that checks generated page body classes plus simulated runtime outline visibility for built chapter pages and fails on unintended empty-outline layouts.
- [x] 2.2 Extend automated tests to cover the regression-guard contract and the new shared script-module integration points.
- [x] 2.3 Add an optional localhost-backed WKWebView replay check for local validation, and harden reader runtime bootstrapping so the replay sees hydrated outline/reference state.

## 3. Figure Fallback Hardening

- [x] 3.1 Harden runtime figure caption annotation with alt-label and short-adjacent-caption fallback handling.
- [x] 3.2 Run book/site verification and mark the change complete with updated task state.
