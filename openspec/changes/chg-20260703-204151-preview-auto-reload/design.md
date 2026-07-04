## Context

The current preview workflow is intentionally simple: `scripts/preview.sh` runs `npm run build:site` once, prints the preview URLs, and starts `scripts/preview_server.py` against `public/`. That keeps the assembled site contract clear, but it also means preview has no long-running build loop and no browser refresh path.

This change touches multiple layers at once:

- shell startup orchestration in `scripts/preview.sh`
- static serving behavior in `scripts/preview_server.py`
- assembled-site rebuild orchestration in a new preview watch script
- preview-focused validation scripts

The repository already treats `public/` as the only assembled output tree, so the solution should preserve that model instead of introducing a second dev server or a separate preview build format.

## Goals / Non-Goals

**Goals:**
- Keep `npm run preview` as the single local preview entrypoint.
- Rebuild the assembled site automatically after render-affecting source changes.
- Refresh open preview pages automatically after a successful rebuild.
- Avoid adding external watch or websocket dependencies when the built-in platform tools are sufficient.
- Preserve the current startup URLs, route structure, and production build output.

**Non-Goals:**
- Preserving in-browser UI state across refreshes.
- Introducing true module-level HMR.
- Replacing `build:site` with partial or route-specific builds.
- Injecting preview reload code into production artifacts on disk.

## Decisions

### Decision: Add a dedicated Node-based preview watcher
The preview command should spawn a dedicated Node script that watches a bounded set of render-affecting roots such as `assets/`, `config/`, `editions/`, `scripts/`, and `theme/`. On changes, it should run the existing assembled-site build command instead of inventing a new build pipeline.

This keeps preview aligned with the same `public/` output users already inspect, and avoids a higher-risk migration to Vite/Webpack or a split `mdbook serve` plus landing-page proxy arrangement.

Alternative considered:
- Recompose preview around multiple dev servers and a proxy. Rejected because it would complicate route ownership and duplicate the existing assembled-site workflow.

### Decision: Serialize rebuilds with debounce and a rerun flag
The watcher should debounce bursts of file events, allow only one rebuild at a time, and remember whether another change arrived while a rebuild was in progress. After the current build finishes, it should run at most one queued rebuild.

This avoids overlapping `build:site` processes from clobbering `public/` and keeps rebuild behavior deterministic when editors emit multiple filesystem events per save.

Alternative considered:
- Fire a new build for every event immediately. Rejected because concurrent full-site builds would race on the same output tree.

### Decision: Use a shared reload token file plus preview-only polling
The watcher and server should communicate through a shared reload token file. The watcher updates the token only after a successful rebuild. The preview server exposes the current token at a preview-only endpoint, and injected browser-side preview code polls that endpoint and triggers `location.reload()` when the token changes.

This design keeps cross-process coordination simple, avoids websocket dependencies, and works for both book pages and generated landing pages with the same mechanism.

Alternative considered:
- Add websocket push from the Python server. Rejected because it increases protocol and process complexity without a practical benefit for whole-page reloads.

### Decision: Inject the preview client at serve time, not build time
The preview server should inject the polling script only into HTML responses it serves when a reload token file is configured. The built HTML files in `public/` should remain unchanged on disk.

This preserves the production artifact contract and keeps preview-only behavior isolated to the preview server.

Alternative considered:
- Teach each generator and theme template to emit preview reload code conditionally. Rejected because it would spread preview-only logic across multiple output producers.

## Risks / Trade-offs

- [Full-site rebuilds may still feel slower than true HMR] -> Accept this because the request is to avoid manual restarts, and the existing assembled-site build is the stable correctness boundary.
- [Filesystem watch events can be noisy or coalesced differently across editors] -> Watch stable top-level roots, debounce events, and queue at most one rerun while a build is active.
- [A rebuild can fail and leave stale content in the browser] -> Do not advance the reload token on failed builds; keep serving the last successful output and print the build failure to stderr.
- [Preview-only HTML injection could accidentally leak into published output] -> Inject only in the Python server response path when the reload token flag is present; do not write modified HTML back to disk.

## Migration Plan

1. Add the OpenSpec proposal, design, tasks, and capability spec for preview auto reload.
2. Update preview-focused tests and source-level assertions to describe the new watch/reload contract.
3. Implement the preview watcher and reload-token coordination.
4. Extend the preview server with preview-only HTML injection and reload-token endpoint handling.
5. Wire the watcher into `scripts/preview.sh` while preserving current LAN-friendly startup output and cleanup behavior.
6. Validate the preview-specific tests plus the narrowest useful assembled-site checks.
