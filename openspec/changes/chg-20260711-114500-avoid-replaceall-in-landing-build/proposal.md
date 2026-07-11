## Why

`npm run preview` currently fails during landing generation in environments where the active JavaScript runtime does not provide `String.prototype.replaceAll`. The failure happens inside `scripts/shared/homepage-outline-icons.mjs`, which means the landing build can break before the preview server ever starts.

This should be fixed with the smallest possible compatibility change: keep the same escaping behavior, but stop relying on `replaceAll` in the landing build path.

## What Changes

- Replace `replaceAll` usage in `scripts/shared/homepage-outline-icons.mjs` with older-runtime-safe global replacements.
- Add a regression assertion so the landing build path does not reintroduce `replaceAll`.

## Capabilities

### Modified Capabilities
- `landing-site-build`: Landing generation remains compatible with older JavaScript runtimes used by preview and local build entrypoints.

## Impact

- Affected source:
  - `scripts/shared/homepage-outline-icons.mjs`
- Affected verification:
  - `scripts/test-site-render.sh`
