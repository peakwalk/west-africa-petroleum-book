## ADDED Requirements

### Requirement: Stakeholder icon rebuilds MUST use acceptance-driven multi-variant selection
The project SHALL rebuild the stakeholder icon package from the approved screenshot reference using multiple candidate approaches per failing icon, then select and publish only the candidates that satisfy the acceptance criteria.

#### Scenario: Failing icons generate multiple reconstruction candidates
- **WHEN** a stakeholder icon fails the acceptance review
- **THEN** the rebuild flow generates at least two candidate variants for that icon
- **THEN** the variants may come from different reconstruction families such as screenshot trace, cleaned proxy vector, or hand-authored SVG
- **THEN** the workflow does not force all icons through one identical reconstruction method

#### Scenario: Final icon selection is based on comparison rather than first output
- **WHEN** multiple candidates exist for a stakeholder icon
- **THEN** the workflow compares those candidates against the screenshot-derived source reference
- **THEN** the final selected version is the candidate that best satisfies quantified comparison and manual review
- **THEN** lower-quality candidates are not silently promoted to final delivery

### Requirement: Final stakeholder icon package MUST pass acceptance as a complete set
The project SHALL not treat the stakeholder icon rebuild as complete until the final package passes completeness checks, frontend SVG checks, special-case rules, and screenshot-fidelity review across the full icon set.

#### Scenario: Special-case icon rules remain enforced
- **WHEN** `oil_drop` is rebuilt
- **THEN** the final SVG preserves the right-side negative-space slit as transparent cutout
- **THEN** the final icon does not collapse into a generic solid drop

#### Scenario: Smooth vector delivery rejects rough trace output
- **WHEN** the final SVGs are reviewed
- **THEN** noisy direct-trace edges, broken line rhythm, and visibly stepped contours cause acceptance failure
- **THEN** only frontend-usable clean vector geometry can pass

#### Scenario: Rebuild loop continues until all icons pass
- **WHEN** any icon still fails the acceptance criteria
- **THEN** the rebuild workflow iterates again for that icon
- **THEN** the package is not accepted as final until every icon passes

### Requirement: Acceptance MUST distinguish baseline trace fidelity from production polish
The project SHALL maintain two acceptance layers: a `baseline` trace-fidelity gate for candidate filtering and a stricter `production` polish gate for polished frontend delivery.

#### Scenario: Baseline acceptance remains useful for candidate filtering
- **WHEN** a rebuilt icon package is checked under the `baseline` profile
- **THEN** the checker validates screenshot similarity, package completeness, special-case negative space rules, and basic frontend SVG safety
- **THEN** passing `baseline` does not by itself imply the icon is polished enough for final delivery

#### Scenario: Production acceptance rejects stroke-like trace silhouettes
- **WHEN** a line-dominant icon such as `regulators`, `governments`, `shield_star`, or `global` is checked under the `production` profile
- **THEN** the delivery must use stroke-led or equivalently hand-controlled vector geometry rather than an evenodd-filled trace silhouette
- **THEN** obvious trace-derived path bloat or line wobble causes production failure even if baseline overlap metrics still pass

#### Scenario: Replacing homepage-facing icons requires production polish
- **WHEN** a stakeholder or topic-card icon is treated as a polished final frontend replacement
- **THEN** that icon set must pass the `production` profile in addition to `baseline`
- **THEN** manual review remains required before the set is considered fully accepted
