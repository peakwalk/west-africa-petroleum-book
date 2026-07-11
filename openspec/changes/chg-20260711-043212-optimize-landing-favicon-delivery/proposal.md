## Why

The landing shell still uses one `240x256` PNG for browser tab icons, shortcut icons, and Apple touch icons. That file is about `45KB`, so every landing route pays more favicon bytes than necessary for normal navigation, even though the primary browser-tab need is only a `32x32` asset.

## What Changes

- Split landing favicon delivery into a small tab favicon PNG and a separate Apple touch icon PNG.
- Update the shared landing head generator to reference the smaller tab icon for `rel="icon"` and `rel="shortcut icon"`, while keeping a dedicated larger PNG for `rel="apple-touch-icon"`.
- Keep the landing shell on PNG assets for favicon compatibility; do not switch favicon delivery to WebP.
- Refresh landing verification so generated pages fail if they fall back to the old oversized shared favicon path.

## Capabilities

### New Capabilities
- `landing-favicon-delivery`: Landing pages use a small tab favicon PNG plus a dedicated Apple touch icon PNG instead of one oversized shared favicon asset.

### Modified Capabilities
- None.

## Impact

- Affected landing source generation: `scripts/shared/landing-shell.mjs`
- Affected landing source assets: `assets/images/upstream-atlas-favicon.png`, `assets/images/upstream-atlas-favicon-32.png`, `assets/images/upstream-atlas-apple-touch-icon.png`
- Affected verification: `tests/test_public_editions.py`, `scripts/test-site-render.sh`
- Affected generated output after rebuild: `public/index.html`, `public/fr/index.html`, `public/chapters/index.html`, `public/fr/chapters/index.html`, `public/*legal*.html`, and the copied favicon assets under `public/assets/images/` plus `public/fr/assets/images/`
