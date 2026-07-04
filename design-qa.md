# Hero Reference-Match QA

- source image path: `/var/folders/y7/ll1_jx7s583dgv6g95hpbx1m0000gn/T/codex-clipboard-e3c67afa-9647-4f61-82d1-3cfaff1bb0b8.png`
- derived hero background path: `/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/assets/images/upstream-atlas-hero-v6-soft-left.webp`
- implementation screenshot path: `/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-2026-07-02-j.png`
- viewport: `1440x900` desktop
- state: homepage default state at top of page
- full-view evidence: `/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-2026-07-02-j.png`
- focused hero evidence: `/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/output/playwright/landing-hero-refmatch-focused-2026-07-02-j.png`

**Findings**
- No actionable `P0` / `P1` / `P2` mismatches remain for this pass. The hero no longer renders the left side as a discrete vertical dark strip; it now uses a continuous deep-blue gradient field that tracks the reference screenshot more closely while preserving text contrast and current platform scale.

**Open Questions**
- None.

**Implementation Checklist**
- Keep the soft-left hero image variant unchanged and adjust only overlay strength and positioning when iterating.
- Re-run desktop screenshot QA if the hero background source, overlay strength, or composition changes again.

**Patches Made In This Pass**
- Replaced the previous hard-edge widened hero image with a soft-left variant so the left dark field is carried by a smooth color transition rather than a near-black vertical slab.
- Shifted the left-side hero shading to a broader radial deep-blue gradient so the dark field rolls in from the edge instead of reading as a column.
- Kept the existing platform photography direction and approximate scale while smoothing the left-to-right gradient behavior.
- Rewired the hero background CSS and render checks to track the soft-left asset.

final result: passed
