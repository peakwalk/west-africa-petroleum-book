## Why

The landing build still copies ten legacy PNG variants from `assets/icons/homepage-cropped/` into both English and French public asset trees even though the landing generators only reference the corresponding WebP files. Those PNGs no longer participate in the runtime contract and add avoidable payload to the built site.

This follow-up cleanup should stay narrow. It should remove only the unused cropped-icon PNG copies, keep the active WebP assets unchanged, and update the directory documentation so it matches the current delivery format.

## What Changes

- Remove the unused PNG files from `assets/icons/homepage-cropped/`.
- Update the cropped-icon directory README to describe the WebP asset contract.
- Add regression checks so the PNG variants stay absent from the source tree and from generated public assets.

## Capabilities

### New Capabilities
- `homepage-cropped-icon-png-cleanup`: The landing source tree and generated asset trees exclude the retired cropped-icon PNG variants while continuing to serve the WebP icon set.

### Modified Capabilities
- None.

## Impact

- Affected source assets removed from `assets/icons/homepage-cropped/`:
  - `icon-audience-operators.png`
  - `icon-audience-policy.png`
  - `icon-audience-research.png`
  - `icon-exploration.png`
  - `icon-fiscal.png`
  - `icon-industry-monitoring.png`
  - `icon-intelligence.png`
  - `icon-production.png`
  - `icon-regulation.png`
  - `icon-research.png`
- Affected documentation: `assets/icons/homepage-cropped/README.md`, `assets/icons/homepage-cropped/README.zh_CN.md`
- Affected verification: `tests/test_public_editions.py`, `scripts/test-site-render.sh`
