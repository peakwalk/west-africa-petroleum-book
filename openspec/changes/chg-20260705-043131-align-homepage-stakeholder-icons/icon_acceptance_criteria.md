# Icon Acceptance Criteria

## Scope

This document defines the acceptance criteria for the trace-based stakeholder icon rebuild work in this change set. It applies to source extraction, vector cleanup, frontend SVG delivery, PNG exports, and preview comparison assets.

All criteria in this document are mandatory unless a later approved change explicitly replaces them.

## Acceptance Levels

### Baseline Trace Fidelity Pass

- Purpose: candidate filtering and screenshot-faithful rebuild validation.
- This level checks whether the package is close enough to the screenshot reference, structurally correct, frontend-safe, and complete.
- Passing `baseline` means the package is suitable for comparison, review, and iteration.
- Passing `baseline` does **not** mean the icons are polished enough for final homepage or topic-card delivery.

### Production Polish Pass

- Purpose: polished final frontend delivery.
- This level requires the package to pass `baseline` first.
- It then adds stricter expectations for optical refinement, stroke semantics, path economy, and trace cleanup.
- Replacing homepage-facing icons should require `production`, not only `baseline`.
- Automated production checks are necessary but not sufficient; manual visual review is still required.

## Pass / Reject Rules

- A rebuilt icon set passes `baseline` only when every icon passes every mandatory `baseline` criterion.
- A rebuilt icon set passes `production` only when every icon passes every mandatory `baseline` criterion, every mandatory `production` criterion, and the final manual review gate.
- A single critical mismatch is sufficient to reject the set.
- "Close enough" is not acceptable when the mismatch changes silhouette, negative space, line quality, or frontend usability.

## 1. Shape Fidelity

- The rebuilt icon silhouette must match the source reference silhouette.
- Internal cutouts, negative-space gaps, and enclosed holes must remain in the same visual positions as the source reference.
- The rebuild must preserve the source's proportion, balance, and visual weight.
- The rebuild must not normalize the source into a generic icon-library style.
- At a `256px` overlay comparison, visible drift on the main contour should stay within `1px`; minor interior detail drift should stay within `2px`.

## 2. Stroke Uniformity, Smoothness, And Optical Correction

- Stroke-based icons must use visually uniform line weight across the full icon.
- Visual stroke-width variation on major strokes must stay within `10%`.
- Curves must be smooth and continuous.
- The icon must not show stair-step edges, spikes, wobble, or accidental sharp corners at `400%` zoom.
- Open line breaks, accidental joins, and inconsistent terminals are not acceptable.

### Additional `production` expectations

- Major visual axes such as crossbeams, stems, rooflines, shield spines, and globe arcs must look intentionally corrected rather than directly inherited from blurred pixels.
- If a shape is supposed to read as straight, circular, or symmetrically arced, it must be rebuilt that way rather than left with trace wobble.
- Automatic trace output may be used to generate a draft, but any direct-trace roughness must be removed from the final delivery.

## 3. Negative Space And Fill Integrity

- Transparent areas must be truly transparent.
- White paint must not be used to fake transparent cutouts.
- Compound paths, masks, clip paths, or `fill-rule="evenodd"` may be used when needed, but the delivered result must remain clean and predictable in browsers.
- Filled icons must keep stable outer contours and stable interior cutouts after export to PNG.

### Special Requirement: `oil_drop`

- The icon must remain a solid dark-blue oil drop, not a generic solid water drop.
- The right-side interior highlight slit must remain as transparent negative space.
- The slit must start from the upper-right interior and curve downward in a way that matches the source reference.
- Removing, straightening, over-widening, or filling this slit is an automatic rejection.

## 4. Required Source-Shape Traits Per Icon

### `regulators`

- Must clearly include the long crossbeam, center node, two hanging pans, center post, and base.
- The center node must remain visually distinct.
- The icon must not collapse into a simplified "scale" pictogram that loses the source proportions.

### `governments`

- Must read as a compact classical government or temple building.
- Must preserve the peaked roof, center body, column rhythm, and layered base.
- It must not drift into a modern bank glyph or a generic courthouse icon.

### `operators`

- Must preserve the central tower, lower supports, side equipment/platform shapes, and the small round or loop-like side structures visible in the source.
- It must not collapse into a simple derrick or triangular tower icon.
- This icon is accepted only if the rebuilt silhouette still reads as the same source device at a glance.

### `shield_star`

- Must preserve the shield crown, lower point, and compact centered star.
- The star must not be enlarged enough to distort the shield balance.

### `global`

- Must preserve the outer circle, latitude lines, and meridian layout from the source reference.
- It must not become a filled circle, a generic globe symbol, or a materially different longitude/latitude pattern.

## 5. Vector Cleanliness And Path Economy

- Final SVG files must contain vector geometry only.
- Embedded bitmap data, base64 image payloads, and raster-wrapped SVG output are not acceptable.
- Paths must be clean enough for frontend maintenance: no accidental specks, no stray fragments, no obvious trace noise.
- Closed filled shapes must remain properly closed.
- SVG files must not keep editor-only metadata that is irrelevant to runtime use.

### Additional `production` expectations

- Automatic trace may generate the draft, but the final delivery must not visibly preserve micro-wobble from the screenshot blur.
- Path data should reflect deliberate vector construction rather than dense trace residue.
- Line-dominant icons should prefer stroke-led geometry, not heavy compound-fill silhouettes pretending to be line icons.

## 6. Frontend Delivery Requirements

- Each icon must be delivered as a standalone SVG file.
- Background must be transparent.
- Stroke-based icons should use:
  - `stroke="currentColor"`
  - `fill="none"`
  - `stroke-linecap="round"`
  - `stroke-linejoin="round"`
  - `vector-effect="non-scaling-stroke"`
- Filled icons should use `fill="currentColor"` unless a different clean vector treatment is required by the source.
- The SVG must render correctly when inlined directly in frontend markup.
- The SVG must not depend on editor-specific namespaces or hidden assets.

### Additional `production` expectations

- `regulators`, `governments`, `shield_star`, and `global` are line-dominant or outline-dominant icons. Their polished final delivery should be stroke-led or otherwise hand-controlled geometry, not an `evenodd`-filled trace silhouette.
- A package that still relies on filled trace contours for those icons may pass `baseline`, but should fail `production`.

## 7. PNG Export Requirements

- Every icon must be exported to transparent PNG at `64`, `128`, `256`, `512`, `1024`, and `2048` pixels.
- Exported PNGs must preserve silhouette, transparency, and negative-space integrity.
- Small-size exports must remain legible and visually stable.
- At `24px`, `32px`, and `64px` visual review, the icon must still read cleanly without muddy edges or merged details.

## 8. Package Completeness

- The package must include:
  - `source_reference/`
  - `svg/`
  - `png/`
  - `preview/`
  - `metadata.json`
  - `review_notes.md`
- Filenames must be stable, explicit, and consistent with the icon names.
- Preview assets must make it possible to compare rebuilt icons against source references without extra manual setup.

## 9. Review Procedure

The reviewer should validate in this order:

1. Run the `baseline` acceptance checks and reject the package immediately if they fail.
2. Compare rebuilt icons against `source_reference` in the compare preview.
3. Inspect each SVG at high zoom for contour fidelity, line consistency, and negative-space correctness.
4. Run or review the `production` acceptance checks.
5. Perform manual polish review for line semantics, optical correction, and trace cleanup.
6. Review PNG exports at both large size and small UI size.
7. Reject the set if any icon fails any mandatory criterion at the required acceptance level.

## 10. Automatic Rejection Conditions

- Main silhouette is visibly different from the source.
- Interior negative space is missing, misplaced, or filled.
- Stroke width is visibly inconsistent.
- Curves show obvious jagged trace artifacts.
- The icon was redesigned instead of rebuilt from the source.
- The SVG contains embedded raster data.
- Small-size PNG output becomes muddy or unreadable.

## 11. Additional `production` Rejection Conditions

- The package passes overlap checks but still looks like direct bitmap tracing.
- A line-dominant icon is delivered as a heavy filled trace silhouette instead of a controlled stroke-led or hand-built vector.
- Major axes or arcs still show visible wobble from the screenshot blur.
- Manual review concludes that the result is faithful but not yet refined enough to match the design reference's finish.
