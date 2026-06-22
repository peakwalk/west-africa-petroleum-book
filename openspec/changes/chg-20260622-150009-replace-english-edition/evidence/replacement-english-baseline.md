# Replacement English Baseline

## Evidence Sources

- Replacement English DOCX: `resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx`
- Replacement English PDF: `resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).pdf`
- Retired English DOCX alias target: `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx`
- Retired English PDF alias target: `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf`
- Current published English navigation source: `editions/en/content/SUMMARY.md`
- Current published French navigation freeze boundary: `editions/fr/content/SUMMARY.md`

Quantitative signals captured from the current workspace:

- Retired English DOCX size: `11,274,269` bytes
- Replacement English DOCX size: `83,721,583` bytes
- Retired English PDF size: `10,094,932` bytes
- Replacement English PDF size: `144,993,188` bytes
- Retired English non-empty paragraph count: about `1,074`
- Replacement English non-empty paragraph count: about `9,135`
- Replacement English figure count from caption-style paragraph scan: `80`
- Replacement English table count from caption-style paragraph scan: `33`

Interpretation:

- The replacement manuscript is not a revision of the current English edition. It is a different book-scale source with materially different structure and asset volume.
- Current English parity assumptions are stale. Running `python3 scripts/check_docx_parity.py --edition en --docx <replacement-docx>` currently yields zero extracted outline/body blocks for every English chapter.

## Replacement Manuscript Structure

### Front Matter Inventory

The replacement manuscript exposes the following pre-body materials before its heading-1 chapter sequence:

1. Title page
   - `Exploration and Production of Petroleum Resources in West Africa: Roles and Responsibilities of Governments and Analysis of Fiscal Regimes`
2. `DISCLAIMER`
3. `Preface`

Notably absent from the extracted replacement front matter:

- a standalone `Foreword`
- a standalone `Abbreviations, Acronyms and Abbreviations` section
- a standalone manuscript `List of Figures`
- a standalone manuscript `List of Tables`

Reader-facing implication:

- `list-of-figures.md` and `list-of-tables.md` may remain as synthetic web reference pages, but they should no longer be treated as manuscript-native front-matter chapters.

### Top-Level Section Inventory

The replacement manuscript exposes 12 heading-1 sections:

1. `General Introduction`
2. `Emerging Petroleum Provinces in West Africa`
3. `West Africa Country Analysis`
4. `National Oil Companies in West Africa`
5. `Hydrocarbon Value Chain`
6. `Upstream Operations and Government Roles`
7. `Petroleum Fiscal Regimes`
8. `West African Fiscal Regimes`
9. `Socio-Political Determinants`
10. `Petroleum Data Management in West Africa`
11. `General Conclusion`
12. `Vision for West Africa 2050`

The raw DOCX TOC styles show a numbering gap between `8.*` and `10.*`. The heading-1 sequence itself is continuous, so the gap is treated as a manuscript-style normalization issue rather than a release blocker. Implementation should prefer heading analysis over blind trust in raw TOC numbering.

### Back Matter Inventory

The replacement manuscript continues after its 12 numbered body chapters with:

1. `Glossary`
2. `Bibliographical References`

Reader-facing implication:

- `General Conclusion` and `Vision for West Africa 2050` belong inside the numbered body-chapter sequence, not inside web-only back matter.

## Old-to-New Topic Mapping

The current English tree and the replacement English manuscript do not map one-to-one. The migration baseline is:

| Current English source | Replacement manuscript target | Migration note |
| --- | --- | --- |
| `cover.md` | synthetic title-page wrapper | Preserve as a reader-facing wrapper around the manuscript title page. |
| `list-of-figures.md` | synthetic web figure index | Preserve as a reader utility with regenerated references, even though the manuscript does not expose a standalone figures chapter. |
| `list-of-tables.md` | synthetic web table index | Preserve as a reader utility with regenerated references, even though the manuscript does not expose a standalone tables chapter. |
| `abbreviations-acronyms-and-abbreviations.md` | no standalone equivalent found | Retire unless later manuscript inspection reveals a hidden appendix. |
| `foreword.md` | no standalone equivalent found | Retire. The replacement manuscript uses `DISCLAIMER` plus `Preface` instead of a standalone foreword. |
| `general-introduction.md` | `General Introduction` | Content survives, but the slug moves into the numbered body-chapter namespace. |
| `chapter-01-value-chain-of-the-hydrocarbon-sector.md` | `Hydrocarbon Value Chain` | Topic survives but title and internal outline change substantially. |
| `chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md` | `Upstream Operations and Government Roles` | Topic survives but scope expands and title changes. |
| `chapter-03-tax-regimes-in-the-petroleum-sector.md` | `Petroleum Fiscal Regimes` | Topic survives with deeper restructuring. |
| `chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md` | `West African Fiscal Regimes` | Topic survives with broader country and modelling coverage. |
| `chapter-05-key-socio-political-determinants-of-oil-sector-performance.md` | `Socio-Political Determinants` | Topic survives with updated structure. |
| `chapter-06-west-africa-in-depth-country-analysis.md` | `West Africa Country Analysis` | Topic survives with larger country set and new internal layout. |
| `general-conclusion.md` | `General Conclusion` | Content survives, but the slug moves into the numbered body-chapter namespace. |
| `glossary.md` | `Glossary` | Preserve the existing semantic slug and replace the body from the replacement manuscript. |
| `bibliographical-references.md` | `Bibliographical References` | Preserve the existing semantic slug and replace the body from the replacement manuscript. |

Net-new replacement-only topics that need dedicated English pages:

- `DISCLAIMER`
- `Emerging Petroleum Provinces in West Africa`
- `National Oil Companies in West Africa`
- `Petroleum Data Management in West Africa`
- `Vision for West Africa 2050`

## English-Only Cutover Boundary

### Mutable During This Change

The following files or areas are expected to change during implementation:

- `editions/en/content/SUMMARY.md`
- `editions/en/content/index.md`
- `editions/en/content/chapters/**`
- `editions/en/content/images/**`
- `editions/en/locale.json`
- `resources/editions/en/reference.docx`
- `resources/editions/en/reference.pdf`
- `scripts/docx_parity/**`
- `scripts/check_docx_parity.py`
- `scripts/build_docx_figure_manifest.py`
- `scripts/check_docx_figures.py`
- `scripts/render_pdf_figures.py`
- `scripts/render_docx_chart_figures.py`
- `scripts/render_docx_shape_figures.py`
- `scripts/render_docx_vector_figures.py`
- `scripts/build_reader_page_meta.mjs`
- `scripts/build_static_reader_sidebar.mjs`
- `scripts/generate-chapters-page.mjs`
- `theme/custom.js`
- `theme/custom.css`
- English-facing tests and assertions that encode the retired English topology

### Frozen During This Change

The following paths are explicit no-touch boundaries:

- `editions/fr/**`
- `resources/editions/fr/reference.docx`
- `resources/editions/fr/reference.pdf`

Shared script changes are allowed only when they are necessary to parse or publish the replacement English edition. Any shared-script edit must be followed by the narrowest French regression check because French files themselves remain frozen.

## Target English Slug Set

This change keeps semantic slugs for front matter, but it preserves the `chapter-` prefix contract for numbered manuscript sections because the current parity, figure, reader-meta, and chapter-library tooling all treat `chapter-*` files as the canonical body-chapter set. The raw TOC numbering gap is normalized into a sequential chapter sequence based on heading-1 order.

Planned English source files:

- `chapters/cover.md`
- `chapters/disclaimer.md`
- `chapters/preface.md`
- `chapters/list-of-figures.md`
- `chapters/list-of-tables.md`
- `chapters/chapter-01-general-introduction.md`
- `chapters/chapter-02-emerging-petroleum-provinces-in-west-africa.md`
- `chapters/chapter-03-west-africa-country-analysis.md`
- `chapters/chapter-04-national-oil-companies-in-west-africa.md`
- `chapters/chapter-05-hydrocarbon-value-chain.md`
- `chapters/chapter-06-upstream-operations-and-government-roles.md`
- `chapters/chapter-07-petroleum-fiscal-regimes.md`
- `chapters/chapter-08-west-african-fiscal-regimes.md`
- `chapters/chapter-09-socio-political-determinants.md`
- `chapters/chapter-10-petroleum-data-management-in-west-africa.md`
- `chapters/chapter-11-general-conclusion.md`
- `chapters/chapter-12-vision-for-west-africa-2050.md`
- `chapters/glossary.md`
- `chapters/bibliographical-references.md`

Notes:

- `cover.md` is retained as a synthetic reader wrapper around the manuscript title page even though the replacement manuscript does not surface `Cover` as a TOC label.
- `disclaimer.md` and `preface.md` come from manuscript-native front matter.
- `list-of-figures.md` and `list-of-tables.md` remain synthetic web utilities rather than manuscript-native chapters.
- Numbered manuscript sections move into the sequential `chapter-XX-...` namespace so batch parity, figure inventory, and reader metadata continue to operate on the English body set without a second body-chapter discovery model.
- `glossary.md` and `bibliographical-references.md` remain semantic back-matter slugs because the replacement manuscript still carries those reference sections after the numbered body chapters.

## Deep-Link Policy for This Change

Decision:

- Preserve only deep links whose slug still matches a real or synthetic replacement front-matter section:
  - `cover.html`
  - `disclaimer.html`
  - `preface.html`
  - `list-of-figures.html`
  - `list-of-tables.html`
  - `glossary.html`
  - `bibliographical-references.html`
- Intentionally break legacy English deep links that point to retired section names or retired chapter numbering, including:
  - `abbreviations-acronyms-and-abbreviations.html`
  - `foreword.html`
  - `general-introduction.html`
  - `general-conclusion.html`
  - `chapter-01-value-chain-of-the-hydrocarbon-sector.html`
  - `chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html`
  - `chapter-03-tax-regimes-in-the-petroleum-sector.html`
  - `chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html`
  - `chapter-05-key-socio-political-determinants-of-oil-sector-performance.html`
  - `chapter-06-west-africa-in-depth-country-analysis.html`

Rationale:

- Preserving those legacy paths would keep the retired six-chapter topology alive as a compatibility shell, which directly conflicts with the replacement-manuscript-first design.
- Sequential `chapter-XX-...` slugs keep the existing body-chapter tooling contract while still dropping the retired six-chapter topology.
- If legacy redirect handling is later required, it should be implemented as a separate explicit compatibility layer after the replacement English structure is stable.
