## Why

`assets/css/landing.css` has grown into a single handwritten stylesheet with more than 2,700 lines. That makes review, isolated edits, and ownership boundaries harder than they need to be, especially now that the repository has explicit file-size guidance for landing-page stylesheets. The current file mixes tokens, header navigation, hero styling, section cards, footer styling, and responsive overrides in one source.

To comply with the new repository rule without changing homepage behavior, the landing-page CSS needs to be reorganized into smaller, coherent source files while preserving the same generated site output and asset references.

## What Changes

- Split `assets/css/landing.css` into smaller landing-page stylesheet modules organized by stable concerns.
- Keep `assets/css/landing.css` as the public entry stylesheet so existing HTML references and asset-version wiring do not change.
- Update site-render validation so it checks the modular CSS structure without weakening the existing visual and structural assertions.

## Capabilities

### New Capabilities
- `landing-stylesheet-organization`: The landing-page styles are maintained as small, coherent handwritten modules while preserving the public stylesheet entrypoint and current rendered behavior.

## Impact

- Affected sources: `assets/css/landing.css`, new sibling landing CSS partials under `assets/css/`
- Affected validation: `scripts/test-site-render.sh`
- Affected generated output indirectly through `npm run build:site`
- No intended change to homepage information architecture, copy, routes, or visual behavior
