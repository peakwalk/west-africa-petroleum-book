## Context

The preview workflow is a thin shell wrapper around `npm run build:site` plus a small Python HTTP server. The current split means the user sees two startup surfaces:

- `scripts/preview.sh` prints the ready URLs
- `scripts/preview_server.py` prints the active serving banner

If only one of those surfaces is updated, the workflow becomes confusing. The same display address therefore needs to flow through both layers.

## Goals / Non-Goals

**Goals:**
- Make `npm run preview` usable for phone testing on the same LAN by default.
- Print an address that a second device can actually open.
- Keep deterministic test coverage for the startup output.
- Preserve explicit host overrides.

**Non-Goals:**
- Discovering or preferring multiple network interfaces.
- Implementing mDNS, QR codes, or automatic device pairing.
- Changing cache headers, routing, or build behavior.

## Decisions

### Decision: Bind to `0.0.0.0` by default
The preview server should listen on all IPv4 interfaces unless the user explicitly overrides `HOST`. This makes the default workflow usable for same-LAN device testing without requiring users to remember an environment variable.

Alternative considered:
- Keep `127.0.0.1` as the default and only document `HOST=0.0.0.0`. Rejected because the user intent here is operational convenience, and the current default is the source of the problem.

### Decision: Separate bind host from display host
When the bind host is a wildcard address such as `0.0.0.0`, that is not the address users should paste into another device. The shell wrapper should therefore compute a display host, and pass it to the Python server so both startup messages stay aligned.

Alternative considered:
- Print the wildcard address verbatim. Rejected because `0.0.0.0` is not a usable destination for phone testing.

### Decision: Add an explicit display-host override for testing
Automatic LAN IP detection is inherently environment-dependent. For deterministic automated checks, the workflow should allow a `PREVIEW_DISPLAY_HOST` override.

Alternative considered:
- Test only the autodetection path. Rejected because CI and local shells often expose different interface availability.

## Risks / Trade-offs

- [Automatic detection may pick the wrong interface on unusual machines] -> Allow explicit `PREVIEW_DISPLAY_HOST` and explicit `HOST` overrides.
- [Binding to all interfaces is broader than loopback] -> Accept this for preview workflows because the user explicitly needs LAN access, and the served content remains local static output.
- [Some machines may fail UDP-based interface detection] -> Fall back to the bind host or loopback-safe output rather than crashing.

## Migration Plan

1. Add the OpenSpec proposal, design, tasks, and capability spec for LAN-friendly preview output.
2. Update `scripts/preview.sh` to default-bind on `0.0.0.0` and compute a display host.
3. Update `scripts/preview_server.py` to accept and print the display host.
4. Extend preview startup assertions to cover the LAN-output contract.
5. Validate the preview build path, site-render assertions, and site build.
