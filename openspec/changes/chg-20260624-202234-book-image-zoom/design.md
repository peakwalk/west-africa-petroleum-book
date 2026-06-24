## Context

The reader already rewrites chapter markup into `.figure-card` structures in `theme/custom.js`. That means the enhancement still needs to run after figure cards are built, but it does not need a custom overlay, gesture system, or internal-scroll lock if the browser itself handles the full-size image view in a new tab.

The figure set mixes raster and vector assets (`webp`, `png`, `svg`), so the design should continue to treat the clicked image URL as the source of truth and avoid any asset-pipeline changes.

## Goals / Non-Goals

**Goals:**
- Let users inspect body figure images more easily than the inline reading width allows.
- Keep the interaction scoped to generated body figure cards only.
- Support both click and keyboard activation.
- Reuse the browser's native image viewing behavior instead of maintaining a custom zoom surface.
- Avoid chapter Markdown, figure-manifest, or asset-pipeline changes.
- Remove the vendored pan/zoom dependency and simplify the runtime.

**Non-Goals:**
- Building an in-page overlay, gallery, carousel, or previous/next navigation for figures.
- Controlling or standardizing browser-native image viewer UI across browsers.
- Enabling zoom behavior for cover art, landing-page assets, sidebar icons, or other non-body images.
- Regenerating or renaming figure assets as part of this feature.

## Decisions

### Decision: Scope eligibility to generated reader figure cards
The enhancement continues to target only `.reader-article .figure-card img`, with an explicit install step that marks eligible images as keyboard-focusable and openable. This keeps the behavior aligned with the reader's generated figure chrome and avoids accidental activation on book-shell or site-marketing images.

Alternative considered:
- Bind to every `.content img`. Rejected because it would affect non-reader and decorative images outside the requested scope.

### Decision: Open the original asset in a new tab
The runtime will open the clicked image URL in a new browser tab via a user-initiated action and let the browser provide the full-size image viewing, zooming, and panning behavior. This removes the need to maintain a custom overlay lifecycle, fit algorithm, gesture system, and close-state model in the theme.

Alternative considered:
- Keep iterating on the in-page overlay viewer. Rejected because the fit and gesture path has already shown higher maintenance cost than the simpler browser-native fallback justifies.

### Decision: Remove the local pan/zoom dependency
Because the browser handles the full-size image tab directly, the theme no longer needs a vendored pan/zoom helper or extra script ordering in `book.toml`.

Alternative considered:
- Keep the vendored helper in case the custom viewer returns later. Rejected because unused runtime dependencies and assertions create avoidable maintenance surface.

## Risks / Trade-offs

- [The reader no longer keeps image inspection inside the chapter tab] -> Accept this trade-off in exchange for simpler and more reliable behavior; the original chapter tab remains available.
- [Browser-native image viewing varies by browser] -> Accept it because this path intentionally delegates the detailed zoom/pan UX to the browser rather than reimplementing it.
- [Popup behavior depends on user-initiated events] -> Trigger the new-tab open only from direct click or keyboard activation.
- [Future content may wrap figure images in links] -> Scope the installer to generated figure-card images and skip images already inside anchors.

## Migration Plan

1. Update the OpenSpec proposal, design, tasks, and capability spec to describe browser-native new-tab image opening.
2. Remove the vendored pan/zoom dependency and its related source-level assertions.
3. Replace the custom viewer implementation in `theme/custom.js` with a lightweight new-tab open handler.
4. Remove obsolete viewer CSS while keeping the focus affordance for keyboard activation.
5. Validate with the narrowest relevant theme and site checks before broader site verification.

## Open Questions

- None for this change.
