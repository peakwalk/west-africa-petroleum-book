## Context

The landing page is published through a static HTML shell that links to `assets/css/landing.css?v=20260701`. That stylesheet is now the main handwritten style surface for the homepage and has accumulated several distinct concerns:
- global tokens and layout primitives,
- header and mobile navigation,
- hero layout and hero variants,
- shared section and card styling,
- discovery and summary modules,
- footer styling,
- and responsive overrides.

The repository's new file-size guidance says landing-page stylesheets should normally stay under 500 lines and that non-trivial edits to already-oversized files should extract coherent partials. The safest way to comply without changing public behavior is to keep `landing.css` as a thin import manifest and move the existing rules into sibling module files that remain in the same directory so relative asset URLs keep working.

`scripts/test-site-render.sh` currently reads `assets/css/landing.css` directly for many assertions. If the entry file becomes an import manifest, the validation script must expand those imports into a combined CSS string before running the existing checks.

## Goals / Non-Goals

**Goals:**
- Reduce `landing.css` to a small entry stylesheet.
- Split the handwritten CSS into coherent modules under the repo's new size guidance.
- Preserve all current asset paths, stylesheet URLs, and rendered homepage behavior.
- Keep validation at the same effective strength after the split.

**Non-Goals:**
- Redesign the homepage.
- Rename the public stylesheet URL.
- Introduce a CSS build pipeline or preprocessor.
- Use the split as an excuse for broad visual cleanup.

## Decisions

### 1. Keep the public entrypoint stable

`assets/css/landing.css` remains the only stylesheet linked by the generated HTML. It becomes an import manifest so no template or asset-version changes are needed.

### 2. Split by durable concern boundaries

The stylesheet will be separated into sibling modules for:
- base tokens and primitives,
- header and navigation,
- hero,
- shared sections and cards,
- discovery and summary modules,
- footer,
- and responsive overrides.

These boundaries match the actual way the homepage evolves and are easier to maintain than arbitrary line-range splitting.

### 3. Keep modules in the same directory as the entry file

The new partial stylesheets stay under `assets/css/` beside `landing.css`. That preserves existing relative `url("../images/...")` and `url("../icons/...")` references without rewriting every asset path for a subdirectory move.

### 4. Validate against expanded CSS, not the thin manifest alone

The site-render script should reconstruct a combined landing CSS string by following local `@import` rules before checking for expected selectors and declarations. That preserves the meaning of the current assertions.

## Risks / Trade-offs

- [Import order mistakes could cause style regressions] -> Preserve source order exactly when splitting and verify with `build:site` plus `test:site`.
- [Validation could weaken if it checks only the manifest] -> Expand imports before assertions and keep the existing checks on the combined CSS text.
- [Some modules could still exceed the new guidance] -> Choose enough modules to keep each handwritten stylesheet comfortably below the threshold.

## Migration Plan

1. Add the OpenSpec artifacts for the stylesheet-organization change.
2. Split `landing.css` into ordered sibling modules and reduce the entry file to imports.
3. Update `scripts/test-site-render.sh` to validate the expanded CSS content.
4. Run `npm run build:site` and `npm run test:site`.

## Open Questions

- None.
