## Why

`npm run preview` is currently optimized for loopback use only. It binds and announces `127.0.0.1`, which makes phone testing awkward even though the preview content itself is safe to serve on a local LAN for ad hoc verification.

## What Changes

- Default the preview server bind host to `0.0.0.0`.
- Detect and print a LAN-accessible display host in startup output.
- Keep support for explicit host overrides and add an explicit display-host override for deterministic testing.
- Make the preview server banner print the same LAN-accessible address as the shell wrapper.

## Capabilities

### New Capabilities
- `preview-lan-output`: `npm run preview` announces a LAN-reachable URL for local-network testing while still serving the same built site assets.

### Modified Capabilities
- None.

## Impact

- Affected source files: `scripts/preview.sh`, `scripts/preview_server.py`, `scripts/test-preview-build.sh`, `scripts/test-site-render.sh`
- No book content, figure manifest, or published asset changes
