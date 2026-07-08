## 1. OpenSpec and failing acceptance

- [x] 1.1 Update the proposal, design, spec, and Chinese companion files so this change documents the iterative multi-variant trace rebuild workflow instead of the old direct-import route.
- [x] 1.2 Add a focused failing acceptance test for the current stakeholder icon rebuild package before changing the generator.

## 2. Multi-variant rebuild tooling

- [x] 2.1 Extend the stakeholder icon rebuild script so each failing icon can emit multiple candidate variants from different reconstruction approaches.
- [x] 2.2 Add candidate comparison outputs that make it possible to review source reference, competing variants, and the selected final version side by side.
- [x] 2.3 Add a dedicated acceptance checker that validates package completeness, SVG semantics, special-case icon rules, and quantified silhouette similarity.

## 3. Rebuild, select, and iterate

- [x] 3.1 Generate at least two candidate variants for every failing icon and select the current best candidate per icon.
- [x] 3.2 Refine any icons that still fail acceptance and rerun the rebuild-review loop until the full package passes.
- [x] 3.3 Refresh the final preview artifacts, metadata, and review notes so they reflect the passing set rather than a failing intermediate package.

## 4. Verify and close

- [x] 4.1 Run the focused acceptance test and any supporting checks against the final package.
- [x] 4.2 Review the final compare preview against the screenshot reference and confirm that all icons now satisfy the acceptance criteria.

## 5. Layered acceptance update

- [x] 5.1 Update the acceptance criteria and checker so they distinguish baseline trace-fidelity acceptance from production polish acceptance.
- [x] 5.2 Re-run the acceptance review under the layered standard and record that the current package passes baseline but not production polish.

## 6. Production polish follow-up

- [x] 6.1 Hand-rebuild the final delivery SVGs so all six icons satisfy the production polish gate rather than only the baseline gate.
- [x] 6.2 Re-run production polish acceptance before treating the rebuilt icons as the final polished delivery set.
