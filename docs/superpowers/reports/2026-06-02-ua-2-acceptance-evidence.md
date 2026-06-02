# UA-2 Acceptance Evidence

Date: 2026-06-02

Scope: Homepage responsive verification and lightweight performance proof for UA-2.

## Verification Commands

- `npm run test:site`
- `npm run build`

Both commands passed on the current working tree.

## Responsive Checks

### Desktop

- Target viewport: `1440x960`
- Observed viewport: `1440x960`
- Navigation layout: `row`
- Hero layout columns: `740px 444px`
- Country grid columns: `289px 289px 289px 289px`
- Country signal grid columns: `114.703px 114.711px`
- Header CTA width: `141.578px`

Conclusion: Desktop preserves the intended two-column hero and four-column country coverage layout.

### Tablet

- Target viewport: `834x1194`
- Observed viewport: `834x1194`
- Navigation layout: `row`
- Hero layout columns: `802px`
- Country grid columns: `802px`
- Country signal grid columns: `371.203px 371.211px`
- Header CTA width: `141.578px`

Conclusion: Tablet collapses the hero and country cards into a single-column reading flow while preserving two-column signal slots inside each country card.

### Mobile

- Target viewport: `390x844`
- Observed viewport: `390x844`
- Navigation layout: `column`
- Hero layout columns: `367.594px`
- Country grid columns: `367.594px`
- Country signal grid columns: `319.203px`
- Header CTA width: `367.594px`

Conclusion: Mobile switches navigation to stacked mode, expands the header CTA to full width, and collapses country signals to a single-column stack.

## Lightweight Performance Proof

### Key Built File Sizes

- `public/index.html`: `26,710` bytes
- `public/assets/css/landing.css`: `16,939` bytes
- `public/assets/images/prototype-hero.jpg`: `113,437` bytes
- `public/assets/images/west-africa-intelligence-overlay.svg`: `2,819` bytes
- `public/assets/images/upstream-atlas-wordmark.png`: `12,303` bytes
- `public/assets/images/upstream-atlas-icon.png`: `4,964` bytes

### Aggregate Notes

- Homepage shell + CSS + hero image + SVG overlay total: `159,905` bytes
- The six measured homepage-critical files above total: `177,172` bytes
- Hero raster payload was reduced from `199,999` bytes to `113,437` bytes, a savings of `86,562` bytes.
- Brand raster assets were reduced from `452,923` bytes to `17,267` bytes, a savings of `435,656` bytes.
- `public/assets` directory size: `1.6M`
- `public/assets` file count: `10`

## Performance Interpretation

- The new petroleum intelligence overlay is low-cost: the SVG adds only `2,819` bytes.
- Homepage shell and CSS remain lightweight relative to the image payload.
- The optimized hero image now carries the largest single-file cost at `113,437` bytes, down from `199,999`.
- Logo assets are no longer the dominant pressure after indexed PNG re-export.
- The main remaining performance weight is now the hero raster image, not the navigation or footer branding.

## Residual Risk

- If stronger performance evidence is required for review, the next optimization target should be the hero raster image before touching layout or typography.
