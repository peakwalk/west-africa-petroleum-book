# Auto Cross-Reference Report

Snapshot date: 2026-06-24

This report records where the runtime body-copy auto-linker is actually active in the published web book as of this snapshot.

## Scope

- Source of truth: rendered `/book/` and `/fr/book/` pages after the reader runtime JavaScript has executed.
- Detection rule: only links rendered as `a.reader-cross-reference-link` count.
- Exclusions by design:
  - `List of Figures`, `List of Tables`, and `List of Equations` pages
  - figure/table/formula card chrome
  - existing anchors
  - headings

This means the report reflects final reader behavior, not raw Markdown pattern matches.

## Verification Method

1. Build the site with `npm run build:site`.
2. Serve `public/` locally.
3. Open the published chapter pages in headless Chrome.
4. Enumerate rendered `a.reader-cross-reference-link` nodes from the final DOM.

## English Edition

Live auto-linked references found: 35

### Page: General Introduction

Source: [chapter-01-general-introduction.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-01-general-introduction.md:73)

- `Chapter 2` at line 73
- `Chapter 3` at line 75
- `Chapter 4` at line 77
- `Chapter 5` at line 79
- `Chapter 6` at line 81
- `Chapter 7` at line 83
- `Chapter 8` at line 85
- `Chapter 9` at line 87
- `Chapter 10` at line 89
- `Chapter 11` at line 91
- `Chapter 12` at line 93

### Page: Hydrocarbon Value Chain

Source: [chapter-05-hydrocarbon-value-chain.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md:55)

- `Table 2` at line 55
- `Table 3` at line 120
- `Figure 8` at line 190
- `Table 4` at line 214
- `Table 5` at line 448
- `Figure 9` at line 745

### Page: Upstream Operations and Government Roles

Source: [chapter-06-upstream-operations-and-government-roles.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-06-upstream-operations-and-government-roles.md:15)

- `Figure 15` at line 15
- `Figure 17` at line 998
- `Figure 18` at line 1010
- `Figure 19` at line 1030
- `Figure 20` at line 1030
- `Figure 22` at line 1112
- `Figure 23` at line 1134
- `Figure 28` at line 1667
- `Figure 29` at line 1669

### Page: West African Fiscal Regimes

Source: [chapter-08-west-african-fiscal-regimes.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/en/content/chapters/chapter-08-west-african-fiscal-regimes.md:590)

- `Section 8.5` at line 590
- `Figure 72` at line 866
- `Figure 73` at line 866
- `Figure 74` at line 866
- `Figure 75` at line 866
- `Figure 76` at line 866
- `Figure 77` at line 866
- `Table 17` at line 1859
- `Figure 79` at line 1859

## French Edition

Live auto-linked references found: 14

### Page: Value Chain of the Hydrocarbon Sector

Source: [chapter-01-value-chain-of-the-hydrocarbon-sector.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md:29)

- `Tableau 1` at line 29
- `Tableau 2` at line 104
- `Figure 4` at line 294

### Page: Different Phases of Upstream Oil and the Roles of States

Source: [chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md:41)

- `Figure 6` at line 41
- `Figure 7` at line 101
- `Figure 9` at line 109
- `Figure 10` at line 119
- `Figure 13` at line 149
- `Figure 15` at line 155
- `Figure 20` at line 608

### Page: Tax Regimes in the Petroleum Sector

Source: [chapter-03-tax-regimes-in-the-petroleum-sector.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md:3)

- `Figure 21` at line 3
- `Figure 22` at line 13
- `Figure 23` at line 39

### Page: Comparative Study of Tax Regimes in Selected West African Countries

Source: [chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md](/Users/edison/workspace/peakwalk/scm/gitlab/africa-book/editions/fr/content/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md:132)

- `Figure 24` at line 132

## Current Boundaries

### Equation and Formula links

The runtime linker now supports `Equation X.Y` and `Formula X.Y`.

As of this snapshot, no live English or French body-copy pages render any numbered equation references that match this contract, so there are currently zero live equation-link hits in the reader.

### Reference index pages

The following pages intentionally render zero `reader-cross-reference-link` nodes because the linker skips `.reference-index` content:

- `list-of-figures.html`
- `list-of-tables.html`
- `list-of-equations.html`

## Why the runtime count is smaller than a raw text scan

A raw Markdown scan will over-count because it sees:

- caption text
- index pages
- figure/table/formula card chrome
- duplicated references inside generated structures

The runtime report is the correct regression baseline because it matches what readers can actually click.
