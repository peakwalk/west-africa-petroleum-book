# DOCX Figure Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic DOCX figure inventory and coverage pipeline that identifies every Figure in the reference manuscript, classifies its source object type, records whether a published asset exists, and exposes the remaining rendering gaps as actionable reports.

**Architecture:** Keep the existing `scripts/docx_parity` package focused on semantic text parity, but add a separate `scripts/docx_figures` package that parses Word OOXML drawing, chart, shape, and media relationships into a manifest. Roll the work out in two phases: first deliver Python 3.9-compatible inventory, manifest, and coverage checks against the live manuscript; then add renderers and markdown sync on top of the manifest in later tasks.

**Tech Stack:** Python 3.9 standard library (`argparse`, `dataclasses`, `json`, `pathlib`, `re`, `unittest`, `xml.etree.ElementTree`, `zipfile`), npm scripts, existing Markdown chapters and image assets

---

## Solution Summary

### Confirmed Boundaries

- `src/chapters/*.md` remains the publishing source.
- `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx` remains the reference source.
- The first implementation slice does not attempt to render missing charts or shape groups; it inventories and reports them.
- The first implementation slice must run on the current local Python 3.9 runtime.
- Complex Word figures must be classified as `chart`, `shape_group`, `vector_media`, `bitmap`, `multi_photo`, or `composite`; they are not to be inferred from front-end adjacency.

### File Map

- `scripts/docx_parity/*.py`
  Modify for Python 3.9-compatible postponed annotations so existing parity tooling runs locally.
- `scripts/docx_figures/__init__.py`
  Stable exports for the new figure inventory package.
- `scripts/docx_figures/model.py`
  Dataclasses for figure records, paragraph object stats, asset status, and coverage diffs.
- `scripts/docx_figures/inventory.py`
  DOCX OOXML parser that walks paragraphs, relationships, captions, and nearby object clusters.
- `scripts/docx_figures/report.py`
  Human-readable and JSON rendering for manifest and coverage diagnostics.
- `scripts/build_docx_figure_manifest.py`
  CLI that writes `src/images/figure-manifest.json`.
- `scripts/check_docx_figures.py`
  CLI that validates manifest coverage against Markdown chapter references and repository assets.
- `src/images/figure-manifest.json`
  Generated manifest capturing figure number, caption, chapter, kind, source objects, and asset status.
- `tests/docx_figures/test_inventory.py`
  Inventory extraction and classification tests.
- `tests/docx_figures/test_report.py`
  Coverage report formatting tests.
- `package.json`
  Add non-destructive local scripts for manifest generation and figure coverage checking.

### Rollout Order

1. Restore local Python compatibility so validation code executes on this workstation.
2. Build the figure inventory package and generate a live manifest for Figure 1 through Figure 32.
3. Add coverage checks that fail when captions exist without corresponding Markdown image references or assets.
4. Promote the manifest and coverage checks into local scripts, but do not yet wire them into `test:site` until rendering gaps are repaired.

---

### Task 1: Restore Python 3.9 Compatibility For Existing Parity Tooling

**Files:**
- Modify: `scripts/docx_parity/extract_docx.py`
- Modify: `scripts/docx_parity/extract_markdown.py`

- [ ] **Step 1: Add postponed annotation evaluation**

Add this first line to both files:

```python
from __future__ import annotations
```

- [ ] **Step 2: Run the existing parity CLI smoke test**

Run:

```bash
python3 scripts/check_docx_parity.py --docx "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx" --summary src/SUMMARY.md --chapters-dir src/chapters --chapter src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md
```

Expected:

```text
... a parity report or pass/fail result, but no TypeError from `| None`
```

### Task 2: Add Figure Inventory Dataclasses And OOXML Parsing

**Files:**
- Create: `scripts/docx_figures/__init__.py`
- Create: `scripts/docx_figures/model.py`
- Create: `scripts/docx_figures/inventory.py`
- Test: `tests/docx_figures/test_inventory.py`

- [ ] **Step 1: Create the figure data model**

Define frozen dataclasses for:

```python
@dataclass(frozen=True)
class FigureObjectStats:
    blip_targets: list[str] = field(default_factory=list)
    chart_targets: list[str] = field(default_factory=list)
    drawing_targets: list[str] = field(default_factory=list)
    anchor_count: int = 0
    inline_count: int = 0
    vshape_count: int = 0
    wps_shape_count: int = 0


@dataclass(frozen=True)
class FigureRecord:
    number: int
    caption: str
    chapter_title: str
    chapter_path: str
    caption_paragraph_index: int
    object_paragraph_start: int
    object_paragraph_end: int
    kind: str
    objects: FigureObjectStats
    published_assets: list[str] = field(default_factory=list)
```

- [ ] **Step 2: Implement DOCX paragraph scanning**

Inventory extraction must:

```python
def build_figure_inventory(
    docx_path: Path,
    chapters_dir: Path,
    summary_path: Path,
) -> list[FigureRecord]:
    ...
```

Rules:
- scan `word/document.xml`
- map `rId` relationships from `word/_rels/document.xml.rels`
- collect per-paragraph stats for `a:blip`, `c:chart`, `v:shape`, `wps:wsp`, `wp:anchor`, `wp:inline`
- detect figure captions from visible text beginning with `Figure <n>:`
- ignore front-matter list-of-figures entries by only inventorying figures after Chapter 1 begins
- map chapter titles to `src/chapters/chapter-*.md` using `src/SUMMARY.md`

- [ ] **Step 3: Classify figures using source-object rules**

Implement:

```python
def classify_figure(stats: FigureObjectStats) -> str:
    if stats.chart_targets:
        return "chart"
    if stats.vshape_count or stats.wps_shape_count:
        if len(stats.blip_targets) > 1:
            return "composite"
        return "shape_group"
    if any(target.endswith((".emf", ".wmf")) for target in stats.blip_targets):
        return "vector_media"
    if len(stats.blip_targets) > 1:
        return "multi_photo"
    if stats.blip_targets:
        return "bitmap"
    return "unknown"
```

- [ ] **Step 4: Write a real-manuscript inventory test**

Add a unittest that asserts the live DOCX inventory includes:
- Figure 24 as `chart`
- Figure 25 as `shape_group` or `composite`
- Figure 31 as `chart`
- Figure 32 as `chart`

### Task 3: Generate A Repository Manifest

**Files:**
- Create: `scripts/build_docx_figure_manifest.py`
- Create: `src/images/figure-manifest.json`
- Test: `tests/docx_figures/test_inventory.py`

- [ ] **Step 1: Write the manifest CLI**

The CLI must:

```python
def main() -> int:
    inventory = build_figure_inventory(...)
    payload = [asdict(record) for record in inventory]
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload)} figure records to {output_path}")
    return 0
```

- [ ] **Step 2: Generate the live manifest**

Run:

```bash
python3 scripts/build_docx_figure_manifest.py
```

Expected:

```text
Wrote 32 figure records to src/images/figure-manifest.json
```

### Task 4: Add Figure Coverage Checks

**Files:**
- Create: `scripts/docx_figures/report.py`
- Create: `scripts/check_docx_figures.py`
- Test: `tests/docx_figures/test_report.py`
- Modify: `package.json`

- [ ] **Step 1: Check for missing chapter image references**

Implement a coverage pass that reports when:
- manifest contains a figure number with no matching Markdown image reference
- Markdown contains a figure image reference whose number is absent from manifest
- caption exists but published asset file is missing from `src/images`

- [ ] **Step 2: Add CLI exit semantics**

`scripts/check_docx_figures.py` must:
- print a readable report by default
- print JSON with `--json`
- exit `1` when any coverage diff exists
- exit `0` only when inventory, Markdown references, and assets all line up

- [ ] **Step 3: Add npm entrypoints**

Add:

```json
{
  "build:docx-figure-manifest": "python3 scripts/build_docx_figure_manifest.py",
  "check:docx-figures": "python3 scripts/check_docx_figures.py --docx \"resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx\" --summary src/SUMMARY.md --chapters-dir src/chapters --manifest src/images/figure-manifest.json"
}
```

### Task 5: Verify The First Slice

**Files:**
- Modify: `tests/docx_figures/test_inventory.py`
- Modify: `tests/docx_figures/test_report.py`

- [ ] **Step 1: Run focused tests**

Run:

```bash
python3 -m unittest tests.docx_figures.test_inventory tests.docx_figures.test_report -v
```

Expected:

```text
OK
```

- [ ] **Step 2: Regenerate the manifest and run the checker**

Run:

```bash
python3 scripts/build_docx_figure_manifest.py
python3 scripts/check_docx_figures.py --docx "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx" --summary src/SUMMARY.md --chapters-dir src/chapters --manifest src/images/figure-manifest.json
```

Expected:

```text
The checker should report the current missing Figure 22-32 asset/reference gaps and exit 1 until rendering and markdown sync are implemented.
```

