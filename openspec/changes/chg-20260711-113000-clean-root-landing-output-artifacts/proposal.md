## Why

The repository still tracks stale landing outputs at the repo root (`index.html` and `fr/index.html`) even though GitHub Pages deploys only the `public/` directory. Those files still contain older PNG-based landing references, which makes asset audits noisy and leaves a misleading second output surface in source control.

The cleanup should remove the stale tracked outputs and make the standalone landing-generation commands default to `public/` so future manual runs do not recreate root-level landing artifacts.

## What Changes

- Delete the tracked root landing outputs that are not part of the deployed site artifact.
- Change standalone landing generation defaults to write under `public/` instead of the repository root.
- Update package script aliases to pass `--output-root public` explicitly for landing, legal, and chapters generation.
- Add regression coverage that keeps root landing outputs out of the tracked source tree and confirms landing pages continue to reference only the allowed PNG assets.

## Capabilities

### New Capabilities
- `root-landing-output-cleanup`: The repository no longer keeps stale root-level landing outputs as tracked files.

### Modified Capabilities
- `landing-site-build`: Standalone landing-generation entrypoints default to the deployed `public/` output tree instead of the repository root.

## Impact

- Affected scripts:
  - `scripts/generate-index-page.mjs`
  - `scripts/generate-legal-pages.mjs`
  - `scripts/generate-chapters-page.mjs`
  - `scripts/test-site-render.sh`
- Affected package aliases:
  - `package.json`
- Affected cleanup targets:
  - `index.html`
  - `fr/index.html`
- Affected regression coverage:
  - `tests/test_public_editions.py`
