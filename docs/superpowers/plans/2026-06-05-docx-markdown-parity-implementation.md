# DOCX Markdown Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic DOCX-vs-Markdown parity gate, repair the current structural drift in live chapter Markdown, and promote the gate into local `test:site` and GitHub Pages publishing.

**Architecture:** Keep `src/chapters/*.md` as the only publishing source, but add a Python standard-library validator that extracts a normalized semantic model from the reference DOCX and from the authored Markdown. Roll the work out in two phases: first implement and verify the validator with isolated fixtures plus opt-in local commands, then repair the live Markdown drift and finally make the parity gate blocking in `test:site` and `.github/workflows/pages.yml`.

**Tech Stack:** Python 3 standard library (`argparse`, `dataclasses`, `pathlib`, `re`, `unittest`, `xml.etree.ElementTree`, `zipfile`), npm scripts, mdBook, existing shell-based render verification

---

## Solution Summary

### Confirmed Boundaries

- Markdown remains the authoritative publishing and editing source.
- `resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx` is the parity reference only.
- The validator compares normalized semantic structure, not raw Markdown text and not `pandoc` output.
- Allowed webpage-only differences are limited to non-semantic wrappers and explicitly marked `parity-ignore` regions.
- The initial implementation must not make CI fail permanently on day one; repair work must happen before the gate is promoted into `test:site`.
- Body parity includes visible paragraphs, list items, and figure/table captions, not just headings.

### File Map

- `scripts/check_docx_parity.py`
  CLI entrypoint for local and CI parity checks.
- `scripts/docx_parity/__init__.py`
  Package marker plus stable exports for the CLI and tests.
- `scripts/docx_parity/model.py`
  Shared dataclasses for outline entries, body blocks, chapters, books, and diffs.
- `scripts/docx_parity/normalize.py`
  Common normalization helpers used on both DOCX and Markdown extraction paths.
- `scripts/docx_parity/extract_docx.py`
  DOCX XML extraction plus Word numbering reconstruction.
- `scripts/docx_parity/extract_markdown.py`
  Summary-aware Markdown semantic extraction plus `parity-ignore` handling.
- `scripts/docx_parity/compare.py`
  Semantic comparison routines and diff typing.
- `scripts/docx_parity/report.py`
  Human-readable and JSON diff formatting.
- `tests/docx_parity/fixtures/docx/*.xml`
  Text fixtures used to synthesize minimal DOCX archives in tests.
- `tests/docx_parity/fixtures/markdown/*.md`
  Markdown and summary fixtures for extractor and comparator tests.
- `tests/docx_parity/test_extract_docx.py`
  Numbering recovery and DOCX semantic extraction tests.
- `tests/docx_parity/test_extract_markdown.py`
  Heading/list/caption/parity-ignore extraction tests.
- `tests/docx_parity/test_compare.py`
  Diff classification and CLI formatting tests.
- `package.json`
  Adds `check:docx-parity` and later promotes it into `test:site`.
- `.github/workflows/pages.yml`
  Switches publishing from `build:site` only to validated `test:site`.
- `src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md`
  Live structural parity repairs.
- `src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md`
  Live structural parity repairs.
- `src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md`
  Live structural parity repairs.
- `src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md`
  Live structural parity repairs.

### Rollout Order

1. Build fixture-backed unit tests and the validator package.
2. Add a non-blocking local CLI command and prove it catches the existing Chapter 1 mismatch.
3. Repair the live Markdown structure until the full-book command passes.
4. Promote the parity command into `test:site` and GitHub Pages CI.

---

### Task 1: Create Red Fixture Tests For Semantic Extraction

**Files:**
- Create: `tests/docx_parity/fixtures/docx/document-numbered.xml`
- Create: `tests/docx_parity/fixtures/docx/numbering-numbered.xml`
- Create: `tests/docx_parity/fixtures/docx/styles-headings.xml`
- Create: `tests/docx_parity/fixtures/markdown/summary-minimal.md`
- Create: `tests/docx_parity/fixtures/markdown/chapter-minimal.md`
- Create: `tests/docx_parity/test_extract_docx.py`
- Create: `tests/docx_parity/test_extract_markdown.py`
- Create: `tests/docx_parity/test_compare.py`

- [ ] **Step 1: Create the minimal DOCX XML fixtures**

```xml
<!-- tests/docx_parity/fixtures/docx/document-numbered.xml -->
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading1"/>
      </w:pPr>
      <w:r><w:t>Chapter 1: Value Chain of the Hydrocarbon Sector</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Intro paragraph.</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading2"/>
        <w:numPr>
          <w:ilvl w:val="1"/>
          <w:numId w:val="9"/>
        </w:numPr>
      </w:pPr>
      <w:r><w:t>The Upstream segment</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading3"/>
        <w:numPr>
          <w:ilvl w:val="2"/>
          <w:numId w:val="9"/>
        </w:numPr>
      </w:pPr>
      <w:r><w:t>Features</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Figure 1: Oil Sector Value Chain</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
```

```xml
<!-- tests/docx_parity/fixtures/docx/numbering-numbered.xml -->
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="7">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:lvlText w:val="%1."/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
    <w:lvl w:ilvl="1">
      <w:start w:val="1"/>
      <w:lvlText w:val="%1.%2-"/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
    <w:lvl w:ilvl="2">
      <w:start w:val="1"/>
      <w:lvlText w:val="%1.%2.%3 -"/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="9">
    <w:abstractNumId w:val="7"/>
  </w:num>
</w:numbering>
```

```xml
<!-- tests/docx_parity/fixtures/docx/styles-headings.xml -->
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/></w:style>
</w:styles>
```

- [ ] **Step 2: Create the minimal Markdown fixtures**

```md
<!-- tests/docx_parity/fixtures/markdown/summary-minimal.md -->
# Summary

- [Chapter 1: Value Chain of the Hydrocarbon Sector](../../../../src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md)
```

```md
<!-- tests/docx_parity/fixtures/markdown/chapter-minimal.md -->
# Chapter 1: Value Chain of the Hydrocarbon Sector

Intro paragraph.

## 1.1- *The Upstream segment*

### 1.1.1 - Features

Figure 1: Oil Sector Value Chain

<!-- parity-ignore:start -->
<div class="reader-helper">ignored helper</div>
<!-- parity-ignore:end -->
```

- [ ] **Step 3: Write the failing unit tests**

```python
# tests/docx_parity/test_extract_docx.py
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.docx_parity.extract_docx import extract_docx_book

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "docx"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def build_fixture_docx() -> Path:
    tmp_dir = Path(tempfile.mkdtemp())
    docx_path = tmp_dir / "fixture.docx"
    with zipfile.ZipFile(docx_path, "w") as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/document.xml", (FIXTURE_DIR / "document-numbered.xml").read_text())
        archive.writestr("word/numbering.xml", (FIXTURE_DIR / "numbering-numbered.xml").read_text())
        archive.writestr("word/styles.xml", (FIXTURE_DIR / "styles-headings.xml").read_text())
    return docx_path


class ExtractDocxTests(unittest.TestCase):
    def test_recovers_multilevel_heading_numbers(self) -> None:
        book = extract_docx_book(build_fixture_docx())
        chapter = book.chapters[0]

        self.assertEqual(chapter.title, "Chapter 1: Value Chain of the Hydrocarbon Sector")
        self.assertEqual(chapter.outline[0].number, "1.1-")
        self.assertEqual(chapter.outline[0].title, "The Upstream segment")
        self.assertEqual(chapter.outline[1].number, "1.1.1-")
        self.assertEqual(chapter.outline[1].title, "Features")
        self.assertEqual(chapter.body[-1].text, "Figure 1: Oil Sector Value Chain")
```

```python
# tests/docx_parity/test_extract_markdown.py
import tempfile
import unittest
from pathlib import Path

from scripts.docx_parity.extract_markdown import extract_markdown_book

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "markdown"


class ExtractMarkdownTests(unittest.TestCase):
    def test_extracts_headings_and_ignores_helper_regions(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-01-value-chain-of-the-hydrocarbon-sector.md"
        chapter_path.write_text((FIXTURE_DIR / "chapter-minimal.md").read_text())
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n- [Chapter 1: Value Chain of the Hydrocarbon Sector](chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md)\n"
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(chapter.title, "Chapter 1: Value Chain of the Hydrocarbon Sector")
        self.assertEqual(chapter.outline[0].number, "1.1-")
        self.assertEqual(chapter.outline[1].number, "1.1.1-")
        self.assertEqual([block.text for block in chapter.body], ["Intro paragraph.", "Figure 1: Oil Sector Value Chain"])
```

```python
# tests/docx_parity/test_compare.py
import unittest

from scripts.docx_parity.compare import compare_books
from scripts.docx_parity.model import BodyBlock, BookSemanticModel, ChapterSemanticModel, OutlineEntry
from scripts.docx_parity.report import render_text_report


class CompareBooksTests(unittest.TestCase):
    def test_reports_outline_number_mismatch(self) -> None:
        docx_book = BookSemanticModel(
            chapters=[
                ChapterSemanticModel(
                    source_path="docx:chapter-1",
                    title="Chapter 1: Value Chain of the Hydrocarbon Sector",
                    outline=[OutlineEntry(level=2, number="1.1-", title="The Upstream segment")],
                    body=[BodyBlock(kind="paragraph", text="Intro paragraph.")],
                )
            ]
        )
        markdown_book = BookSemanticModel(
            chapters=[
                ChapterSemanticModel(
                    source_path="src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md",
                    title="Chapter 1: Value Chain of the Hydrocarbon Sector",
                    outline=[OutlineEntry(level=2, number="1.", title="The Upstream segment")],
                    body=[BodyBlock(kind="paragraph", text="Intro paragraph.")],
                )
            ]
        )

        diffs = compare_books(docx_book, markdown_book)

        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0].diff_type, "outline.number_mismatch")
        self.assertIn("Promote this item to a real section heading", render_text_report(diffs))
```

- [ ] **Step 4: Run the unit tests to verify they fail before implementation**

Run: `python3 -m unittest discover -s tests/docx_parity -p 'test_*.py'`

Expected: FAIL with `ModuleNotFoundError` or missing symbol errors for `scripts.docx_parity.extract_docx`, `extract_markdown`, `compare`, or `render_text_report`.

- [ ] **Step 5: Commit the red tests**

```bash
git add tests/docx_parity
git commit -m "test: add red DOCX parity fixtures"
```

---

### Task 2: Implement Shared Semantic Models And Normalization

**Files:**
- Create: `scripts/docx_parity/__init__.py`
- Create: `scripts/docx_parity/model.py`
- Create: `scripts/docx_parity/normalize.py`
- Test: `tests/docx_parity/test_compare.py`

- [ ] **Step 1: Add the shared dataclasses**

```python
# scripts/docx_parity/model.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutlineEntry:
    level: int
    number: str
    title: str


@dataclass(frozen=True)
class BodyBlock:
    kind: str
    text: str


@dataclass(frozen=True)
class ChapterSemanticModel:
    source_path: str
    title: str
    outline: list[OutlineEntry] = field(default_factory=list)
    body: list[BodyBlock] = field(default_factory=list)


@dataclass(frozen=True)
class BookSemanticModel:
    chapters: list[ChapterSemanticModel] = field(default_factory=list)


@dataclass(frozen=True)
class ParityDiff:
    chapter_path: str
    diff_type: str
    docx_value: str
    markdown_value: str
    hint: str
```

- [ ] **Step 2: Add normalization helpers shared by both extractors**

```python
# scripts/docx_parity/normalize.py
import re

INLINE_MARKUP_RE = re.compile(r"[*_`]+")
WHITESPACE_RE = re.compile(r"\s+")
HEADING_NUMBER_RE = re.compile(r"^(?P<number>\d+(?:\.\d+)*[.-])\s*(?P<title>.+)$")


def normalize_visible_text(value: str) -> str:
    stripped = INLINE_MARKUP_RE.sub("", value)
    collapsed = WHITESPACE_RE.sub(" ", stripped.replace("\u00a0", " "))
    return collapsed.strip()


def normalize_heading_number(value: str) -> str:
    compact = normalize_visible_text(value).replace(" -", "-").replace(". ", ".")
    return compact


def split_heading_label(raw_heading: str) -> tuple[str, str]:
    normalized = normalize_visible_text(raw_heading)
    match = HEADING_NUMBER_RE.match(normalized)
    if not match:
        return "", normalized
    return normalize_heading_number(match.group("number")), match.group("title").strip()
```

- [ ] **Step 3: Export the shared types and helpers**

```python
# scripts/docx_parity/__init__.py
from .compare import compare_books
from .extract_docx import extract_docx_book
from .extract_markdown import extract_markdown_book
from .report import render_json_report, render_text_report

__all__ = [
    "compare_books",
    "extract_docx_book",
    "extract_markdown_book",
    "render_json_report",
    "render_text_report",
]
```

- [ ] **Step 4: Re-run the tests and confirm the failure moves to the missing extractors**

Run: `python3 -m unittest discover -s tests/docx_parity -p 'test_*.py'`

Expected: FAIL with import errors for `extract_docx`, `extract_markdown`, `compare`, or `report`, not with missing dataclasses or helper functions.

- [ ] **Step 5: Commit the shared model layer**

```bash
git add scripts/docx_parity/__init__.py scripts/docx_parity/model.py scripts/docx_parity/normalize.py
git commit -m "feat: add DOCX parity semantic model"
```

---

### Task 3: Implement Direct DOCX Extraction And Word Numbering Recovery

**Files:**
- Create: `scripts/docx_parity/extract_docx.py`
- Test: `tests/docx_parity/test_extract_docx.py`

- [ ] **Step 1: Implement numbering-map reconstruction and paragraph text extraction**

```python
# scripts/docx_parity/extract_docx.py
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from .model import BodyBlock, BookSemanticModel, ChapterSemanticModel, OutlineEntry
from .normalize import normalize_heading_number, normalize_visible_text

W_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

HEADING_STYLES = {
    "Heading1": 1,
    "Heading2": 2,
    "Heading3": 3,
    "Heading4": 4,
    "Heading5": 5,
    "Heading6": 6,
}


def _read_xml(archive: ZipFile, member: str) -> ET.Element:
    return ET.fromstring(archive.read(member))


def _build_numbering_map(numbering_root: ET.Element) -> dict[str, dict[int, str]]:
    abstract_levels: dict[str, dict[int, str]] = {}
    for abstract in numbering_root.findall("w:abstractNum", W_NS):
        abstract_id = abstract.attrib[f"{{{W_NS['w']}}}abstractNumId"]
        level_map: dict[int, str] = {}
        for level in abstract.findall("w:lvl", W_NS):
            ilvl = int(level.attrib[f"{{{W_NS['w']}}}ilvl"])
            level_map[ilvl] = level.find("w:lvlText", W_NS).attrib[f"{{{W_NS['w']}}}val"]
        abstract_levels[abstract_id] = level_map

    numbering_map: dict[str, dict[int, str]] = {}
    for num in numbering_root.findall("w:num", W_NS):
        num_id = num.attrib[f"{{{W_NS['w']}}}numId"]
        abstract_id = num.find("w:abstractNumId", W_NS).attrib[f"{{{W_NS['w']}}}val"]
        numbering_map[num_id] = abstract_levels[abstract_id]
    return numbering_map


def _paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for node in paragraph.findall(".//w:t", W_NS):
        if node.text:
            parts.append(node.text)
    return normalize_visible_text("".join(parts))


def _style_level(paragraph: ET.Element) -> int | None:
    style_node = paragraph.find("w:pPr/w:pStyle", W_NS)
    if style_node is None:
        return None
    return HEADING_STYLES.get(style_node.attrib[f"{{{W_NS['w']}}}val"])


def _num_pr(paragraph: ET.Element) -> ET.Element | None:
    return paragraph.find("w:pPr/w:numPr", W_NS)
```

- [ ] **Step 2: Implement displayed-number reconstruction and chapter assembly**

```python
# scripts/docx_parity/extract_docx.py
def _render_number(level_template: str, counters: dict[int, int]) -> str:
    rendered = level_template
    for level, value in counters.items():
        rendered = rendered.replace(f"%{level + 1}", str(value))
    rendered = rendered.replace(". ", ".").replace(" -", "-").strip()
    if rendered.endswith(" -"):
        rendered = rendered[:-2] + "-"
    return normalize_heading_number(rendered)


def extract_docx_book(docx_path: str | Path) -> BookSemanticModel:
    docx_path = Path(docx_path)
    with ZipFile(docx_path) as archive:
        document_root = _read_xml(archive, "word/document.xml")
        numbering_root = _read_xml(archive, "word/numbering.xml")

    numbering_map = _build_numbering_map(numbering_root)
    counters: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    chapters: list[ChapterSemanticModel] = []
    current_title = ""
    current_outline: list[OutlineEntry] = []
    current_body: list[BodyBlock] = []
    current_path = "docx:front-matter"

    for paragraph in document_root.findall(".//w:body/w:p", W_NS):
        text = _paragraph_text(paragraph)
        if not text:
            continue

        level = _style_level(paragraph)
        num_pr = _num_pr(paragraph)

        if level == 1:
            if current_title:
                chapters.append(
                    ChapterSemanticModel(
                        source_path=current_path,
                        title=current_title,
                        outline=current_outline,
                        body=current_body,
                    )
                )
            current_title = text
            current_path = f"docx:{len(chapters) + 1}"
            current_outline = []
            current_body = []
            continue

        if level and num_pr is not None:
            num_id = num_pr.find("w:numId", W_NS).attrib[f"{{{W_NS['w']}}}val"]
            ilvl = int(num_pr.find("w:ilvl", W_NS).attrib[f"{{{W_NS['w']}}}val"])
            num_counters = counters[num_id]
            num_counters[ilvl] += 1
            for deeper in list(num_counters.keys()):
                if deeper > ilvl:
                    num_counters[deeper] = 0
            number = _render_number(numbering_map[num_id][ilvl], num_counters)
            current_outline.append(OutlineEntry(level=level, number=number, title=text))
            continue

        if num_pr is not None:
            kind = "list_item"
        elif text.startswith("Figure ") or text.startswith("Table "):
            kind = "caption"
        else:
            kind = "paragraph"
        current_body.append(BodyBlock(kind=kind, text=text))

    if current_title:
        chapters.append(
            ChapterSemanticModel(
                source_path=current_path,
                title=current_title,
                outline=current_outline,
                body=current_body,
            )
        )

    return BookSemanticModel(chapters=chapters)
```

- [ ] **Step 3: Run the DOCX extractor tests**

Run: `python3 -m unittest tests.docx_parity.test_extract_docx -v`

Expected: PASS

- [ ] **Step 4: Run the full unit suite and confirm the next failure is the Markdown path**

Run: `python3 -m unittest discover -s tests/docx_parity -p 'test_*.py'`

Expected: FAIL only on `extract_markdown`, `compare`, or `report`.

- [ ] **Step 5: Commit the DOCX extractor**

```bash
git add scripts/docx_parity/extract_docx.py
git commit -m "feat: recover DOCX heading numbering for parity checks"
```

---

### Task 4: Implement Summary-Aware Markdown Extraction With `parity-ignore`

**Files:**
- Create: `scripts/docx_parity/extract_markdown.py`
- Test: `tests/docx_parity/test_extract_markdown.py`

- [ ] **Step 1: Parse summary order and chapter file references**

```python
# scripts/docx_parity/extract_markdown.py
import re
from pathlib import Path

from .model import BodyBlock, BookSemanticModel, ChapterSemanticModel, OutlineEntry
from .normalize import normalize_visible_text, split_heading_label

SUMMARY_LINK_RE = re.compile(r"^\s*-\s+\[(?P<title>.+?)\]\((?P<path>.+?)\)\s*$")
LIST_ITEM_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+(?P<text>.+)$")
PARITY_IGNORE_START = "<!-- parity-ignore:start -->"
PARITY_IGNORE_END = "<!-- parity-ignore:end -->"


def _summary_entries(summary_path: Path, chapters_dir: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for raw_line in summary_path.read_text().splitlines():
        match = SUMMARY_LINK_RE.match(raw_line)
        if not match:
            continue
        relative_path = Path(match.group("path"))
        chapter_path = (summary_path.parent / relative_path).resolve()
        entries.append((match.group("title"), chapter_path))
    return entries
```

- [ ] **Step 2: Implement heading, paragraph, caption, and ignore-block extraction**

```python
# scripts/docx_parity/extract_markdown.py
def _strip_ignored_regions(lines: list[str]) -> list[str]:
    kept: list[str] = []
    ignoring = False
    for line in lines:
        if PARITY_IGNORE_START in line:
            ignoring = True
            continue
        if PARITY_IGNORE_END in line:
            ignoring = False
            continue
        if not ignoring:
            kept.append(line)
    return kept


def _parse_chapter(chapter_path: Path) -> ChapterSemanticModel:
    lines = _strip_ignored_regions(chapter_path.read_text().splitlines())
    title = ""
    outline: list[OutlineEntry] = []
    body: list[BodyBlock] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = normalize_visible_text(" ".join(paragraph_lines))
        paragraph_lines.clear()
        if text:
            kind = "caption" if text.startswith("Figure ") or text.startswith("Table ") else "paragraph"
            body.append(BodyBlock(kind=kind, text=text))

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            title = normalize_visible_text(stripped[2:])
            continue
        if stripped.startswith("## ") or stripped.startswith("### ") or stripped.startswith("#### "):
            flush_paragraph()
            hashes, raw_heading = stripped.split(" ", 1)
            number, heading_title = split_heading_label(raw_heading)
            outline.append(OutlineEntry(level=len(hashes), number=number, title=heading_title))
            continue
        list_match = LIST_ITEM_RE.match(stripped)
        if list_match:
            flush_paragraph()
            body.append(BodyBlock(kind="list_item", text=normalize_visible_text(list_match.group("text"))))
            continue
        if stripped.startswith("![" ):
            flush_paragraph()
            continue
        paragraph_lines.append(stripped)

    flush_paragraph()
    return ChapterSemanticModel(source_path=str(chapter_path), title=title, outline=outline, body=body)


def extract_markdown_book(summary_path: str | Path, chapters_dir: str | Path) -> BookSemanticModel:
    summary_path = Path(summary_path)
    chapters_dir = Path(chapters_dir)
    chapters = [_parse_chapter(chapter_path) for _, chapter_path in _summary_entries(summary_path, chapters_dir)]
    return BookSemanticModel(chapters=chapters)
```

- [ ] **Step 3: Run the Markdown extractor tests**

Run: `python3 -m unittest tests.docx_parity.test_extract_markdown -v`

Expected: PASS

- [ ] **Step 4: Run the full unit suite and confirm the remaining failure is compare/report**

Run: `python3 -m unittest discover -s tests/docx_parity -p 'test_*.py'`

Expected: FAIL only on `compare_books` or `render_text_report`.

- [ ] **Step 5: Commit the Markdown extractor**

```bash
git add scripts/docx_parity/extract_markdown.py
git commit -m "feat: add Markdown semantic extraction for parity checks"
```

---

### Task 5: Implement Comparison, Reporting, And The Non-Blocking CLI

**Files:**
- Create: `scripts/docx_parity/compare.py`
- Create: `scripts/docx_parity/report.py`
- Create: `scripts/check_docx_parity.py`
- Modify: `package.json`
- Test: `tests/docx_parity/test_compare.py`

- [ ] **Step 1: Implement structured diff classification**

```python
# scripts/docx_parity/compare.py
from .model import BookSemanticModel, ParityDiff


def compare_books(docx_book: BookSemanticModel, markdown_book: BookSemanticModel) -> list[ParityDiff]:
    diffs: list[ParityDiff] = []

    if len(docx_book.chapters) != len(markdown_book.chapters):
        diffs.append(
            ParityDiff(
                chapter_path="src/SUMMARY.md",
                diff_type="outline.chapter_count_mismatch",
                docx_value=str(len(docx_book.chapters)),
                markdown_value=str(len(markdown_book.chapters)),
                hint="Align SUMMARY chapter coverage with the reference DOCX before comparing chapter bodies.",
            )
        )

    for docx_chapter, markdown_chapter in zip(docx_book.chapters, markdown_book.chapters):
        if docx_chapter.title != markdown_chapter.title:
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="outline.chapter_title_mismatch",
                    docx_value=docx_chapter.title,
                    markdown_value=markdown_chapter.title,
                    hint="Align the chapter title with the reference DOCX.",
                )
            )

        if len(docx_chapter.outline) != len(markdown_chapter.outline):
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="outline.entry_count_mismatch",
                    docx_value=str(len(docx_chapter.outline)),
                    markdown_value=str(len(markdown_chapter.outline)),
                    hint="Align the number of section headings in this chapter before checking individual labels.",
                )
            )

        for docx_outline, markdown_outline in zip(docx_chapter.outline, markdown_chapter.outline):
            if docx_outline.level != markdown_outline.level:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.level_mismatch",
                        docx_value=f"L{docx_outline.level} {docx_outline.number} {docx_outline.title}",
                        markdown_value=f"L{markdown_outline.level} {markdown_outline.number} {markdown_outline.title}",
                        hint="Restore the heading depth so DOCX and Markdown use the same section hierarchy.",
                    )
                )
            if docx_outline.number != markdown_outline.number:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.number_mismatch",
                        docx_value=f"{docx_outline.number} {docx_outline.title}",
                        markdown_value=f"{markdown_outline.number} {markdown_outline.title}",
                        hint="Promote this item to a real section heading and preserve the DOCX numbering label.",
                    )
                )
            if docx_outline.title != markdown_outline.title:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.title_text_mismatch",
                        docx_value=docx_outline.title,
                        markdown_value=markdown_outline.title,
                        hint="Match the visible heading text to the reference DOCX.",
                    )
                )

        if len(docx_chapter.body) != len(markdown_chapter.body):
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="body.block_count_mismatch",
                    docx_value=str(len(docx_chapter.body)),
                    markdown_value=str(len(markdown_chapter.body)),
                    hint="Align the number of visible paragraph/list/caption blocks before checking sequence content.",
                )
            )

        if [(block.kind, block.text) for block in docx_chapter.body] != [(block.kind, block.text) for block in markdown_chapter.body]:
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="body.sequence_mismatch",
                    docx_value=" | ".join(f"{block.kind}:{block.text}" for block in docx_chapter.body[:5]),
                    markdown_value=" | ".join(f"{block.kind}:{block.text}" for block in markdown_chapter.body[:5]),
                    hint="Compare the visible paragraph/list/caption sequence and repair the first drift point.",
                )
            )

    return diffs
```

- [ ] **Step 2: Implement report rendering and CLI wiring**

```python
# scripts/docx_parity/report.py
import json

from .model import ParityDiff


def render_text_report(diffs: list[ParityDiff]) -> str:
    lines: list[str] = []
    for diff in diffs:
        lines.extend(
            [
                diff.chapter_path,
                f"  type: {diff.diff_type}",
                f"  docx:      {diff.docx_value}",
                f"  markdown:  {diff.markdown_value}",
                f"  hint: {diff.hint}",
            ]
        )
    return "\n".join(lines)


def render_json_report(diffs: list[ParityDiff]) -> str:
    return json.dumps([diff.__dict__ for diff in diffs], indent=2, ensure_ascii=False)
```

```python
# scripts/check_docx_parity.py
import argparse
from pathlib import Path

from scripts.docx_parity import compare_books, extract_docx_book, extract_markdown_book, render_json_report, render_text_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Markdown semantic parity against the reference DOCX.")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--chapters-dir", required=True)
    parser.add_argument("--chapter", help="Limit validation to a single Markdown chapter path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    docx_book = extract_docx_book(Path(args.docx))
    markdown_book = extract_markdown_book(Path(args.summary), Path(args.chapters_dir))
    if args.chapter:
        chapter_path = str(Path(args.chapter))
        markdown_book = type(markdown_book)(chapters=[chapter for chapter in markdown_book.chapters if chapter.source_path == chapter_path])
        chapter_index = next(index for index, chapter in enumerate(extract_markdown_book(Path(args.summary), Path(args.chapters_dir)).chapters) if chapter.source_path == chapter_path)
        docx_book = type(docx_book)(chapters=[docx_book.chapters[chapter_index]])
    diffs = compare_books(docx_book, markdown_book)
    if diffs:
        print(render_json_report(diffs) if args.json else render_text_report(diffs))
        return 1
    print("DOCX parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Add a non-blocking local npm command without changing `test:site` yet**

```json
{
  "scripts": {
    "check:docx-parity": "python3 scripts/check_docx_parity.py --docx \"resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx\" --summary src/SUMMARY.md --chapters-dir src/chapters",
    "test:site": "sh scripts/test-site-render.sh"
  }
}
```

- [ ] **Step 4: Run the unit suite and then prove the CLI catches the current Chapter 1 drift**

Run: `python3 -m unittest discover -s tests/docx_parity -p 'test_*.py'`

Expected: PASS

Run: `python3 scripts/check_docx_parity.py --docx "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx" --summary src/SUMMARY.md --chapters-dir src/chapters --chapter src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md`

Expected: FAIL with at least one `outline.number_mismatch` mentioning `src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md`.

- [ ] **Step 5: Commit the comparator and CLI**

```bash
git add scripts/check_docx_parity.py scripts/docx_parity/compare.py scripts/docx_parity/report.py package.json
git commit -m "feat: add local DOCX parity validator command"
```

---

### Task 6: Repair Chapter 1 And Chapter 2 Structural Drift Until The Validator Passes

**Files:**
- Modify: `src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md`
- Modify: `src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md`
- Test: `scripts/check_docx_parity.py`

- [ ] **Step 1: Convert Chapter 1 pseudo-headings from list items and blockquotes into real headings**

```md
<!-- src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md -->
## 1.1- *The Upstream segment*

### 1.1.1 - Features

## 1.2- *The midstream segment*

### 1.2.1- Characteristics

## 1.3- *Le segment Aval (downstream)*

### 1.3.1- Characteristics
```

Apply those replacements at the current drift points where the file still contains:

```md
1.  ***The Upstream segment***
1.  *The **midstream segment***
> **1.2.1- Characteristics**
1.  ***Le segment Aval (downstream)***
> **1.3.1- Characteristics**
```

- [ ] **Step 2: Convert Chapter 2 phase headings and subheadings into real section structure**

```md
<!-- src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md -->
## 2.1- *Pre-licensing phase*

### 2.1.1- Definition of the concept

### 2.1.2- Strategy for awarding petroleum licences or authorizations

### 2.1.3- Financing of pre-licensing phase investments

### 2.1.4- Importance of the pre-licensing phase and responsibilities of the State

## 2.2- *Exploration phase*

### 2.2.1- Exploration methods and strategies
```

Use the same pattern for the later Chapter 2 phase blocks that are still rendered as ordered-list items, especially the current `Development`, `Production`, `Abandonment`, and `Summary of ...` pseudo-headings.

- [ ] **Step 3: Run the chapter-scoped validator after each repair and stop only when both files are clean**

Run: `python3 scripts/check_docx_parity.py --docx "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx" --summary src/SUMMARY.md --chapters-dir src/chapters --chapter src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md`

Expected: PASS

Run: `python3 scripts/check_docx_parity.py --docx "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx" --summary src/SUMMARY.md --chapters-dir src/chapters --chapter src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md`

Expected: PASS

Run: `npm run check:docx-parity`

Expected: FAIL first on Chapter 3 or Chapter 4 after Chapter 1 and Chapter 2 are repaired; it must no longer report Chapter 1 or Chapter 2 structural list-heading mismatches.

- [ ] **Step 4: Commit the first live-content repair batch**

```bash
git add src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md
git commit -m "fix: restore chapter 1 and 2 heading parity"
```

---

### Task 7: Repair Chapter 3 And Chapter 4 Structural Drift And Finish The Full-Book Cleanup

**Files:**
- Modify: `src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md`
- Modify: `src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md`
- Modify: `src/chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.md` only if the validator reports remaining diffs
- Modify: `src/chapters/chapter-06-west-africa-in-depth-country-analysis.md` only if the validator reports remaining diffs
- Test: `scripts/check_docx_parity.py`

- [ ] **Step 1: Restore Chapter 3 section hierarchy**

```md
<!-- src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md -->
## 3.3- *The contractual system*

### 3.3.1- The Production Sharing Contract (PPC)

### 3.3.2- Service Contracts

## 3.4- *Structure of Oil Tax Systems in West Africa*

## 3.5- *Contractual frameworks in West Africa*
```

Apply those replacements at the current drift points where the file still contains:

```md
> ***3.3- The contractual system*:**
1.  **The Production Sharing Contract (PPC)**
1.  **Service Contracts**
4.  ***Structure of Oil Tax Systems in West Africa***
5.  ***Contractual frameworks in West Africa***
```

- [ ] **Step 2: Restore Chapter 4 section hierarchy**

```md
<!-- src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md -->
## 4.2- *Key tax elements applied in selected West African countries*

### 4.2.1- Redevance ad valorem (royalty)

## 4.3- *In-depth analysis of tax regimes by country*

### 4.3.1- Nigeria

## 4.4- *State/Contractor income associated with the tax system in selected West African countries*
```

Also convert the later `Analysis and interpretations`, `On the overall State/Contracting Party cash flows`, and `Partial conclusion` pseudo-headings to real `##` or `###` headings using the exact numbering labels reported by `npm run check:docx-parity`.

- [ ] **Step 3: Re-run the full validator and resolve all residual diffs before moving on**

Run: `npm run check:docx-parity`

Expected: PASS

If the validator still reports Chapter 5 or Chapter 6 drift, repair those files in the same style before leaving this task; do not promote the CI gate while any chapter still fails.

- [ ] **Step 4: Commit the second live-content repair batch**

```bash
git add src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md src/chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.md src/chapters/chapter-06-west-africa-in-depth-country-analysis.md
git commit -m "fix: restore remaining chapter heading parity"
```

---

### Task 8: Promote DOCX Parity Into `test:site` And GitHub Pages Publishing

**Files:**
- Modify: `package.json`
- Modify: `.github/workflows/pages.yml`
- Test: `scripts/test-site-render.sh`
- Test: `scripts/check_docx_parity.py`

- [ ] **Step 1: Make `test:site` run parity before the render assertions**

```json
{
  "scripts": {
    "check:docx-parity": "python3 scripts/check_docx_parity.py --docx \"resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx\" --summary src/SUMMARY.md --chapters-dir src/chapters",
    "test:site": "npm run check:docx-parity && sh scripts/test-site-render.sh"
  }
}
```

- [ ] **Step 2: Make the Pages workflow validate before upload**

```yaml
# .github/workflows/pages.yml
      - name: Validate site
        run: npm run test:site

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: public
```

Remove the old `Build site` step that runs `npm run build:site`, because `scripts/test-site-render.sh` already builds `public/` before asserting on the output.

- [ ] **Step 3: Run the full local verification stack**

Run: `npm run test:site`

Expected: PASS

Run: `npm run build:site`

Expected: PASS

- [ ] **Step 4: Commit the gate promotion**

```bash
git add package.json .github/workflows/pages.yml
git commit -m "ci: enforce DOCX parity before publishing"
```
