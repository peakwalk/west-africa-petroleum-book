## 1. OpenSpec and test contract

- [x] 1.1 Add the cross-reference-linker proposal and capability spec
- [x] 1.2 Add failing source-level assertions for the new reader cross-reference linker contract

## 2. Reader implementation

- [x] 2.1 Implement a runtime body-copy cross-reference linker in `theme/custom.js`
- [x] 2.2 Reuse existing figure/table anchors, current-page section headings, and sidebar chapter routes as link targets
- [x] 2.3 Keep unresolved references as plain text and avoid relinking inside existing anchors or caption cards
- [x] 2.4 Extend the linker to support `Equation X.Y` and `Formula X.Y` references against numbered formula anchors

## 3. Verification

- [x] 3.1 Run the targeted Python theme tests
- [x] 3.2 Run `npm run build:site`
- [x] 3.3 Run `sh scripts/test-site-render.sh`
- [x] 3.4 Re-run the targeted theme test and site-render assertions for equation-link support
