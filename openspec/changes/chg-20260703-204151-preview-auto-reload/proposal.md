## Why

`npm run preview` currently performs a one-shot `build:site` and then serves static files. Any CSS, chapter content, template, image, or script change that affects rendering requires stopping the process and starting it again, which makes routine layout and content iteration unnecessarily slow.

## What Changes

- Add a preview watch process that observes render-affecting source paths while `npm run preview` is running.
- Re-run `npm run build:site` automatically after relevant file changes, with serialized rebuilds so overlapping edits do not corrupt the assembled output.
- Add a preview-only browser reload mechanism so served HTML pages refresh automatically after a successful rebuild.
- Keep the existing preview routes, LAN-friendly startup output, and static `public/` artifact model unchanged.
- Extend preview-focused validation to cover the watch/reload contract.

## Capabilities

### New Capabilities
- `preview-auto-reload`: `npm run preview` watches render-affecting source files, rebuilds the assembled site after relevant changes, and refreshes connected preview pages after successful rebuilds.

### Modified Capabilities
- None.

## Impact

- Affected sources: `scripts/preview.sh`, `scripts/preview_server.py`, new preview watch orchestration under `scripts/`
- Affected validation: `scripts/test-preview-build.sh`, `scripts/test-preview-cache.sh`, `scripts/test-site-render.sh`
- No new external runtime dependency is intended
- No intended change to published routes, production HTML output, or figure/content source structure
