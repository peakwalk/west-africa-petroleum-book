## 1. OpenSpec and source-level checks

- [x] 1.1 Add the proposal, design, and `preview-lan-output` capability spec for LAN-friendly preview startup output.
- [x] 1.2 Add or update source-level assertions for the preview bind host, display host, and startup banner contract.

## 2. Preview startup behavior

- [x] 2.1 Default `scripts/preview.sh` to bind on `0.0.0.0`.
- [x] 2.2 Detect a LAN-reachable display host when the bind host is a wildcard, with an explicit override for deterministic testing.
- [x] 2.3 Pass the display host through to `scripts/preview_server.py` so its banner matches the wrapper output.

## 3. Verification

- [x] 3.1 Run the targeted preview build/startup test(s).
- [x] 3.2 Run `sh scripts/test-site-render.sh`.
- [x] 3.3 Run the narrowest useful site build/test command needed to confirm preview changes do not affect the built reader output.
