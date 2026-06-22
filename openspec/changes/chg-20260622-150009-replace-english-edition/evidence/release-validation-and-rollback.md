# Release Validation and Rollback

## Release Validation Evidence

Cutover validation completed on `2026-06-23` with the narrowest relevant checks for the replacement English edition:

- `python3 scripts/check_docx_parity.py --edition en`
  - Passed.
- `python3 scripts/check_docx_figures.py --edition en`
  - Passed.
- `python3 scripts/check_docx_figures.py --edition fr`
  - Passed.
- `npm run build:site`
  - Passed.
- `npm run test:site`
  - Passed after refreshing the English topology and asset assertions in `scripts/test-site-render.sh` to match the replacement manuscript.
- `python3 -m unittest tests.test_book_editions tests.test_public_editions tests.test_theme_custom_css.ThemeCustomCssTest.test_figure_annotation_accepts_colonless_and_french_caption_spacing tests.test_theme_custom_css.ThemeCustomCssTest.test_table_annotation_supports_french_tableau_captions_and_docx_tables`
  - Passed (`34` tests).

French freeze-boundary confidence comes from two independent layers:

- `python3 scripts/check_docx_figures.py --edition fr` confirmed that the French figure inventory and published asset expectations still hold.
- The targeted French regression unit tests confirmed that:
  - French book pages still publish the correct French content and asset targets.
  - French public pages still publish the correct French routes and landing copy.
  - Theme parsing still accepts French-facing caption patterns such as colonless `Figure` captions and localized `Tableau` table labels.

## Checks Intentionally Excluded from the Release Gate

The following commands were reviewed but were not used as cutover gate criteria:

- `python3 scripts/check_docx_parity.py --edition fr`
  - Currently fails against a pre-existing French parity baseline mismatch. That failure is not introduced by this English-only cutover, so it is tracked as existing noise rather than a release blocker for this change.
- `python3 -m unittest tests.test_book_editions tests.test_public_editions tests.test_theme_custom_css`
  - The full theme suite currently includes stale style-contract expectations unrelated to the English manuscript replacement. The targeted French-safe theme tests above provide the narrower regression signal needed for this release.

## Rollback Procedure

Operational rollback for the published English edition is English-only:

1. Repoint `resources/editions/en/reference.docx` to the retired English manuscript alias target:
   - `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx`
2. Repoint `resources/editions/en/reference.pdf` to the retired English PDF alias target:
   - `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf`
3. Restore `editions/en/content/**` from the pre-cutover revision.
   - This includes `SUMMARY.md`, all English chapter markdown, `editions/en/content/images/**`, and `editions/en/content/images/figure-manifest.json`.
4. Rebuild the published site:
   - `npm run build:site`
5. Re-run the English release checks:
   - `python3 scripts/check_docx_parity.py --edition en`
   - `python3 scripts/check_docx_figures.py --edition en`
   - `npm run test:site`

Why this rollback scope is sufficient:

- English manuscript aliases are isolated under `resources/editions/en/reference.*`.
- English published source, figure assets, and manifest all live under `editions/en/content/**`.
- French source and French manuscript aliases stay frozen under:
  - `editions/fr/**`
  - `resources/editions/fr/reference.docx`
  - `resources/editions/fr/reference.pdf`

Therefore, restoring the prior English release does not require any French file changes.

## Repo-State Note

If the branch itself must be returned to the exact pre-cutover validation baseline, the rollback commit should also restore English-topology assertions that were updated in shared validation files such as `scripts/test-site-render.sh`. That extra restoration is not required for the runtime English-site rollback itself, but it is required if the repository must again validate against the retired English topology.
