## Why

The current stakeholder icon rebuild package can now clear the coarse screenshot-fidelity gate, but it still does not satisfy the level of polish expected from the supplied design reference. The remaining problem is no longer “does it look like the screenshot at all?” but “is it refined enough to ship as a polished frontend icon set?”

The acceptance model therefore needs to change. A single pass/fail gate is no longer sufficient because the present package can satisfy baseline overlap-driven checks while still looking too trace-derived, too heavy, or too generic. The project needs one acceptance layer for candidate selection and another for polished final delivery.

## What Changes

- Split acceptance into `baseline` trace-fidelity acceptance and `production` polish acceptance.
- Keep `baseline` acceptance focused on screenshot alignment, negative space, frontend safety, and package completeness so it remains useful for candidate filtering.
- Add a stricter `production` polish gate for optical refinement, stroke semantics, path economy, and manual review before the icons are treated as a polished final delivery.
- Update the automated acceptance checker and tests so the current package still passes `baseline` but explicitly fails `production` until the icons are hand-refined.
- Record the new layered acceptance model in the change proposal, design, spec, tasks, and acceptance review artifacts.

## Capabilities

### New Capabilities
- `homepage-stakeholder-icon-alignment`: The project can generate and review a trace-rebuilt stakeholder icon package whose final SVG and PNG assets are selected from multiple candidate approaches and pass the approved acceptance criteria.

### Modified Capabilities
- None.

## Impact

- Affected rebuild tooling: `scripts/build_stakeholder_icons_trace_rebuild.py`
- Affected verification: a new dedicated acceptance checker and its focused test coverage
- Affected review artifacts: preview grids, comparison previews, metadata, and review notes under `artifacts/stakeholder_icons_trace_rebuild/`
- Affected OpenSpec artifacts: proposal, design, spec, tasks, acceptance criteria, and acceptance review notes for this change
