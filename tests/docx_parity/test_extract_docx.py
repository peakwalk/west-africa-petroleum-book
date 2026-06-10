import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.docx_parity.extract_docx import (
    extract_docx_book,
    extract_docx_chapter_by_anchors,
)

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
        archive.writestr(
            "word/document.xml",
            (FIXTURE_DIR / "document-numbered.xml").read_text(encoding="utf-8"),
        )
        archive.writestr(
            "word/numbering.xml",
            (FIXTURE_DIR / "numbering-numbered.xml").read_text(encoding="utf-8"),
        )
        archive.writestr(
            "word/styles.xml",
            (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
        )
    return docx_path


class ExtractDocxTests(unittest.TestCase):
    def test_recovers_multilevel_heading_numbers(self) -> None:
        book = extract_docx_book(build_fixture_docx())
        chapter = book.chapters[0]

        self.assertEqual(
            chapter.title, "Chapter 1: Value Chain of the Hydrocarbon Sector"
        )
        self.assertEqual(chapter.outline[0].number, "1.1-")
        self.assertEqual(chapter.outline[0].title, "The Upstream segment")
        self.assertEqual(chapter.outline[1].number, "1.1.1-")
        self.assertEqual(chapter.outline[1].title, "Features")
        self.assertEqual(chapter.body[-1].text, "Figure 1: Oil Sector Value Chain")

    def test_reuses_current_section_context_when_num_id_changes(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-section-restart.docx"
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr(
                "word/document.xml",
                (FIXTURE_DIR / "document-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(chapter.outline[0].number, "2.1-")
        self.assertEqual(chapter.outline[1].number, "2.1.1-")
        self.assertEqual(chapter.outline[2].number, "2.1.2-")
        self.assertEqual(chapter.outline[3].number, "2.1.3-")

    def test_respects_non_default_start_values_for_top_level_sections(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-top-level-starts.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.1- Design principles</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading2"/>
        <w:numPr>
          <w:ilvl w:val="1"/>
          <w:numId w:val="56"/>
        </w:numPr>
      </w:pPr>
      <w:r><w:t>Key tax elements applied in selected West African countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading2"/>
        <w:numPr>
          <w:ilvl w:val="1"/>
          <w:numId w:val="57"/>
        </w:numPr>
      </w:pPr>
      <w:r><w:t>Partial conclusion</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
"""
        numbering = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="8">
    <w:lvl w:ilvl="1">
      <w:start w:val="4"/>
      <w:lvlText w:val="%1.%2-"/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="9">
    <w:lvl w:ilvl="1">
      <w:start w:val="7"/>
      <w:lvlText w:val="%1.%2-"/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="56">
    <w:abstractNumId w:val="8"/>
  </w:num>
  <w:num w:numId="57">
    <w:abstractNumId w:val="9"/>
  </w:num>
</w:numbering>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr("word/numbering.xml", numbering)
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(chapter.outline[0].number, "4.1-")
        self.assertEqual(chapter.outline[1].number, "4.4-")
        self.assertEqual(chapter.outline[2].number, "4.7-")

    def test_reconciles_parent_heading_number_from_literal_child_prefix(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-parent-prefix-reconcile.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.1- Design principles of the flow diagram associated with the oil contract</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="Heading2"/>
        <w:numPr>
          <w:ilvl w:val="1"/>
          <w:numId w:val="33"/>
        </w:numPr>
      </w:pPr>
      <w:r><w:t>Key tax elements applied in selected West African countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading3"/></w:pPr>
      <w:r><w:t>4.2.1- Redevance ad valorem (royalty)</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
"""
        numbering = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="14">
    <w:lvl w:ilvl="0">
      <w:start w:val="4"/>
      <w:lvlText w:val="%1."/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
    <w:lvl w:ilvl="1">
      <w:start w:val="1"/>
      <w:lvlText w:val="%1.%2."/>
      <w:numFmt w:val="decimal"/>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="33">
    <w:abstractNumId w:val="14"/>
  </w:num>
</w:numbering>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr("word/numbering.xml", numbering)
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(chapter.outline[0].number, "4.1-")
        self.assertEqual(chapter.outline[1].number, "4.2-")
        self.assertEqual(chapter.outline[2].number, "4.2.1-")

    def test_normalizes_pre_heading_figure_spillover_into_single_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-figure-spillover.docx"
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr(
                "word/document.xml",
                (FIXTURE_DIR / "document-figure-spillover.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Intro paragraph.",
                "Figure 5: Different phases of upstream oil",
                "Body paragraph after heading.",
            ],
        )

    def test_normalizes_inline_figure_spillover_into_single_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-inline-figure-spillover.docx"
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr(
                "word/document.xml",
                (FIXTURE_DIR / "document-inline-figure-spillover.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(chapter.outline[0].number, "2.1-")
        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Body paragraph before figure.",
                "Figure 6: Process for Assigning Oil Block to the IPC for Petroleum Exploration and Development",
                "Body paragraph after figure.",
            ],
        )

    def test_preserves_duplicated_formula_paragraph_before_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-duplicated-formula-before-caption.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.1- Design principles of the flow diagram associated with the oil contract</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Post Royalty Revenue = Gross Revenue – RoyaltyPost Royalty Revenue = Gross Revenue – Royalty</w:t></w:r></w:p>
    <w:p><w:r><w:t>Table 5 below shows the proportions of royalties adopted in the oil regulations of selected West African countries.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Table 5: Summary of ad valorem royalty rates applied in selected West African countries</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "Post Royalty Revenue = Gross Revenue - Royalty",
                "Table 5 below shows the proportions of royalties adopted in the oil regulations of selected West African countries.",
                "Table 5: Summary of ad valorem royalty rates applied in selected West African countries",
            ],
        )

    def test_ignores_short_graphic_labels_when_caption_follows(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-short-graphic-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.1- Pre-licensing phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Body paragraph before figure.</w:t></w:r></w:p>
    <w:p><w:r><w:t>b</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 8: 3D acquisition principle (a) and seismic cube (b)</w:t></w:r></w:p>
    <w:p><w:r><w:t>Well PositioningExploratoryWell PositioningExploratory</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 9: Seismic amplitude anomalies showing Brightspots and Flatspots</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Body paragraph before figure.",
                "Figure 8: 3D acquisition principle (a) and seismic cube (b)",
                "Figure 9: Seismic amplitude anomalies showing Brightspots and Flatspots",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_ignores_post_caption_graphic_label_clusters(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-post-caption-graphic-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 3: Tax Regimes in the Petroleum Sector</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>3.2- The concession system</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 23: Classification of tax regimes</w:t></w:r></w:p>
    <w:p><w:r><w:t>ArgentinaBrazilVenezuelaPhilippines…ArgentinaBrazilVenezuelaPhilippines…</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 3: Tax Regimes in the Petroleum Sector",
            start_anchor="Chapter intro paragraph.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Chapter intro paragraph.",
                "Lead-in paragraph.",
                "Figure 23: Classification of tax regimes",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_ignores_pre_caption_flowchart_labels(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-pre-caption-flowchart-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.4- State/Contractor income associated with the tax system in selected West African countries</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>STATE</w:t></w:r></w:p>
    <w:p><w:r><w:t>10</w:t></w:r></w:p>
    <w:p><w:r><w:t>Post-royalty income: 90</w:t></w:r></w:p>
    <w:p><w:r><w:t>Total gross cash flow of the contractor</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 25: Simplified organizational chart showing the share of the State and the Contractor in the taxation associated with the CPP of Benin</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries",
            start_anchor="Chapter intro paragraph.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Chapter intro paragraph.",
                "Lead-in paragraph.",
                "Figure 25: Simplified organizational chart showing the share of the State and the Contractor in the taxation associated with the CPP of Benin",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_ignores_streamer_label_clusters(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-streamer-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.2- Exploration phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>bbaaMultiple qv streamersMultiple qv streamersSourceSource</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 8: 3D acquisition principle (a) and seismic cube (b)</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 2: Different Phases of Upstream Oil and the Roles of States",
            start_anchor="Chapter intro paragraph.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Chapter intro paragraph.",
                "Lead-in paragraph.",
                "Figure 8: 3D acquisition principle (a) and seismic cube (b)",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_ignores_immediate_pre_caption_titlecase_labels(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-immediate-pre-caption-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.2- Exploration phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 8: 3D acquisition principle (a) and seismic cube (b)</w:t></w:r></w:p>
    <w:p><w:r><w:t>Well PositioningExploratoryWell PositioningExploratory</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 9: Seismic amplitude anomalies showing Brightspots and Flatspots</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 2: Different Phases of Upstream Oil and the Roles of States",
            start_anchor="Chapter intro paragraph.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Chapter intro paragraph.",
                "Lead-in paragraph.",
                "Figure 8: 3D acquisition principle (a) and seismic cube (b)",
                "Figure 9: Seismic amplitude anomalies showing Brightspots and Flatspots",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_ignores_semantic_flowchart_clusters_before_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-semantic-flowchart-cluster.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.4- State/Contractor income associated with the tax system in selected West African countries</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>CONTACTING REGIME FISCALGross income: 100Royalty : 10%Cost Stop70%Total net income12,156314,85Oil profit: 27Profit sharing Oil55/45%Gross cash flow77,8522,1512,6224,38PART34,10 %65,9% FLOW CHART BENIN</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 25: Simplified organizational chart showing the share of the State and the Contractor in the taxation associated with the CPP of Benin</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries",
            start_anchor="Chapter intro paragraph.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Chapter intro paragraph.",
                "Lead-in paragraph.",
                "Figure 25: Simplified organizational chart showing the share of the State and the Contractor in the taxation associated with the CPP of Benin",
                "Body paragraph after figure.",
            ],
        )

    def test_ignores_bare_figure_number_placeholders(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-bare-figure-placeholder.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 30: Simplified diagram showing the share of the State and the Contractor resulting from the taxation associated with the CPP of Niger</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 30 :</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "Figure 30: Simplified diagram showing the share of the State and the Contractor resulting from the taxation associated with the CPP of Niger",
                "Body paragraph after figure.",
            ],
        )

    def test_preserves_deduped_caption_paragraph_before_following_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-deduped-caption.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 1: Value Chain of the Hydrocarbon Sector</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>1.1- The Upstream segment</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 2: a and b Map showing the MSGBC BasinFigure 2: a and b Map showing the MSGBC Basin</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 3: Map showing the sedimentary basins of Mali and Niger</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figures.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "Figure 2: a and b Map showing the MSGBC Basin",
                "Figure 3: Map showing the sedimentary basins of Mali and Niger",
                "Body paragraph after figures.",
            ],
        )

    def test_book_extraction_ignores_post_caption_concatenated_label_clusters(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-post-caption-concatenated-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 3: Tax Regimes in the Petroleum Sector</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Intro paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 21: Economic Value of Hydrocarbon Resources</w:t></w:r></w:p>
    <w:p><w:r><w:t>ECONOMIC VALUE OF RESOURCESExploitability (Quantity of Resources, Geological Environment and Facilities)Market ConditionsCrude oil priceTax regimeLaw, Regulations</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body paragraph after figure.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Intro paragraph.",
                "Figure 21: Economic Value of Hydrocarbon Resources",
                "Body paragraph after figure.",
            ],
        )

    def test_chapter_anchor_extraction_stops_at_next_heading_one(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-chapter-boundary.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 1: Value Chain of the Hydrocarbon Sector</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Intro paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 4: Synthetic diagram showing the different oil cuts</w:t></w:r></w:p>
    <w:p><w:r><w:t>0 to 80-100°C0 to 80-100°C</w:t></w:r></w:p>
    <w:p><w:r><w:t>120 to 180°C120 to 180°C</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Next chapter intro.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 1: Value Chain of the Hydrocarbon Sector",
            start_anchor="Intro paragraph.",
            end_anchor="Next chapter intro.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Intro paragraph.",
                "Figure 4: Synthetic diagram showing the different oil cuts",
            ],
        )

    def test_chapter_anchor_extraction_stops_at_split_chapter_marker(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-split-chapter-marker.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 1: Value Chain of the Hydrocarbon Sector</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Intro paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 4: Synthetic diagram showing the different oil cuts</w:t></w:r></w:p>
    <w:p><w:r><w:t>0 to 80-100°C0 to 80-100°C</w:t></w:r></w:p>
    <w:p><w:r><w:t>120 to 180°C120 to 180°C</w:t></w:r></w:p>
    <w:p><w:r><w:t>Chapter 2</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>DIFFERENT PHASES OF UPSTREAM OIL AND THE ROLES OF STATES</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Next chapter intro.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 1: Value Chain of the Hydrocarbon Sector",
            start_anchor="Intro paragraph.",
            end_anchor="Next chapter intro.",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Intro paragraph.",
                "Figure 4: Synthetic diagram showing the different oil cuts",
            ],
        )

    def test_chapter_anchor_extraction_matches_literal_heading_titles_for_start_and_end(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-heading-anchor-titles.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading3"/></w:pPr>
      <w:r><w:t>4.3.1- Nigeria</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Earlier chapter paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 6: West Africa: In-Depth Country Analysis</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Chapter 6 intro.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>6.1- Nigeria</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Nigeria paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>6.2- Ghana</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Ghana paragraph.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 6: West Africa: In-Depth Country Analysis",
            start_anchor="Nigeria",
            end_anchor="Ghana",
        )
        chapter = book.chapters[0]

        self.assertEqual([entry.number for entry in chapter.outline], ["6.1-"])
        self.assertEqual([entry.title for entry in chapter.outline], ["Nigeria"])
        self.assertEqual([block.text for block in chapter.body], ["Nigeria paragraph."])

    def test_chapter_anchor_extraction_falls_back_when_docx_has_no_target_chapter_marker(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-anchor-no-chapter-marker.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Intro paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>1.1- The Upstream segment</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Body paragraph.</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Chapter 1: Value Chain of the Hydrocarbon Sector",
            start_anchor="Intro paragraph.",
            end_anchor=None,
        )
        chapter = book.chapters[0]

        self.assertEqual([entry.number for entry in chapter.outline], ["1.1-"])
        self.assertEqual([entry.title for entry in chapter.outline], ["The Upstream segment"])
        self.assertEqual([block.text for block in chapter.body], ["Intro paragraph.", "Body paragraph."])

    def test_splits_merged_formula_and_label_paragraphs(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-merged-formulas.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.2- Exploration phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>P(prospect) = P(source rock) x P(reservoir) x P(trap)P(prospect) = P(source rock) x P(reservoir) x P(trap)</w:t></w:r></w:p>
    <w:p><w:r><w:t>Waterproof trap + waterproof coverWaterproof trap + waterproof coverPorosity and permeability of reservoir rockPorosity and permeability of reservoir rockGeological hazardsGeological hazards</w:t></w:r></w:p>
    <w:p><w:r><w:t>V</w:t></w:r></w:p>
    <w:p><w:r><w:t>HcP = GRV x N/G x Ø x Shc x 1/FVFVHcP = GRV x N/G x Ø x Shc x 1/FVF</w:t></w:r></w:p>
    <w:p><w:r><w:t>IB</w:t></w:r></w:p>
    <w:p><w:r><w:t>Cs = ∑Deposit Area x Deposit Thickness</w:t></w:r></w:p>
    <w:p><w:r><w:t>STIIOP = GRV x N/G x Ø x So x 1/BoAssociated gas in place = STOIIP x GORSTIIOP = GRV x N/G x Ø x So x 1/BoAssociated gas in place = STOIIP x GOR</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "P(prospect) = P(source rock) x P(reservoir) x P(trap)",
                "Waterproof trap + waterproof cover",
                "Porosity and permeability of reservoir rock",
                "Geological hazards",
                "VHcP = GRV x N/G x Ø x Shc x 1/FVF",
                "IBCs = ∑Deposit Area x Deposit Thickness",
                "STIIOP = GRV x N/G x Ø x So x 1/Bo",
                "Associated gas in place = STOIIP x GOR",
            ],
        )

    def test_splits_repeated_equation_labels_into_separate_paragraphs(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-repeated-equation-labels.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 4: Comparative Study of Tax Regimes in Selected West African Countries</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>4.1- Design principles of the flow diagram associated with the oil contract</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Lead-in paragraph.</w:t></w:r></w:p>
    <w:p><w:r><w:t>R-Factor=Cumulative Revenue/Cumulative CostR-Factor = (Cumulative Revenue - Cumulative Opex) / Cumulative CapexR-Factor = (Cumulative Revenues - Cumulative Profits) / (Cumulative Investments + Cumulative Opex)R-Factor=Cumulative Net Revenue/Cumulative CostsR-Factor=Cumulative Revenue/Cumulative CostR-Factor = (Cumulative Revenue - Cumulative Opex) / Cumulative CapexR-Factor = (Cumulative Revenues - Cumulative Profits) / (Cumulative Investments + Cumulative Opex)R-Factor=Cumulative Net Revenue/Cumulative Costs</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "R-Factor=Cumulative Revenue/Cumulative Cost",
                "R-Factor = (Cumulative Revenue - Cumulative Opex) / Cumulative Capex",
                "R-Factor = (Cumulative Revenues - Cumulative Profits) / (Cumulative Investments + Cumulative Opex)",
                "R-Factor=Cumulative Net Revenue/Cumulative Costs",
            ],
        )

    def test_splits_heading_and_list_items_merged_into_single_paragraph(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-merged-list-cluster.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.3- Development phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>INTEGRATION ANDMODELING</w:t></w:r></w:p>
    <w:p><w:r><w:t>Tank Models and Understanding of the Tank</w:t></w:r></w:p>
    <w:p><w:r><w:t>EVALUATION DES OPTIONS DE RECUPERATIONRecovery Methods (Primary, Secondary, and Tertiary)Types/types of wells (production, injection and observation/horizontal, vertical, inclined, etc.)Etc</w:t></w:r></w:p>
    <w:p><w:r><w:t>Tank Performance Prediction</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            [
                "paragraph",
                "paragraph",
                "paragraph",
                "paragraph",
                "list_item",
                "list_item",
                "list_item",
                "paragraph",
            ],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "INTEGRATION AND",
                "MODELING",
                "Tank Models and Understanding of the Tank",
                "EVALUATION DES OPTIONS DE RECUPERATION",
                "Recovery Methods (Primary, Secondary, and Tertiary)",
                "Types/types of wells (production, injection and observation/horizontal, vertical, inclined, etc.)",
                "Etc",
                "Tank Performance Prediction",
            ],
        )

    def test_preserves_semantic_callouts_before_following_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-semantic-callouts.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.3- Development phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>CAPEX, OPEX, RiskCAPEX, OPEX, Risk</w:t></w:r></w:p>
    <w:p><w:r><w:t>ECONOMIC EVALUATION AND DECISIONSECONOMIC EVALUATION AND DECISIONS</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 17: Methodology Tank EvaluationFigure 17: Methodology Tank Evaluation</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 18: Diagram showing a reservoir model (Vilgeir Dalen, StatoilHydro, 2007)</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "paragraph", "caption", "caption"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "CAPEX, OPEX, Risk",
                "ECONOMIC EVALUATION AND DECISIONS",
                "Figure 17: Methodology Tank Evaluation",
                "Figure 18: Diagram showing a reservoir model (Vilgeir Dalen, StatoilHydro, 2007)",
            ],
        )

    def test_ignores_figure_17_reservoir_methodology_cluster(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-figure-17-methodology-cluster.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 2: Different Phases of Upstream Oil and the Roles of States</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>2.3- Development phase</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Excavated material, cores, seismic data, logging, well tests, etc.</w:t></w:r></w:p>
    <w:p><w:r><w:t>RAW DATA COLLECTION</w:t></w:r></w:p>
    <w:p><w:r><w:t>Descriptive elements of the reservoir</w:t></w:r></w:p>
    <w:p><w:r><w:t>PROCESSING AND INTERPRETATION OF THE DATA COLLECTED</w:t></w:r></w:p>
    <w:p><w:r><w:t>Tank Models and Understanding of the Tank</w:t></w:r></w:p>
    <w:p><w:r><w:t>CAPEX, OPEX, Risk</w:t></w:r></w:p>
    <w:p><w:r><w:t>ECONOMIC EVALUATION AND DECISIONS</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 17: Methodology Tank Evaluation</w:t></w:r></w:p>
    <w:p><w:r><w:t>Figure 18: Diagram showing a reservoir model (Vilgeir Dalen, StatoilHydro, 2007)</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Figure 17: Methodology Tank Evaluation",
                "Figure 18: Diagram showing a reservoir model (Vilgeir Dalen, StatoilHydro, 2007)",
            ],
        )

    def test_preserves_source_credit_lines_before_later_table_caption(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-source-credits.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Chapter 1: Value Chain of the Hydrocarbon Sector</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>1.1- The Upstream segment</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Data Ministries</w:t></w:r></w:p>
    <w:p><w:r><w:t>RPS Energy Report, 2006</w:t></w:r></w:p>
    <w:p><w:r><w:t>According to Trading Economics, the daily oil production of selected West African countries is as shown in Table 2.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Table 2: Daily production of selected West African countries and reserves estimates</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Data Ministries",
                "RPS Energy Report, 2006",
                "According to Trading Economics, the daily oil production of selected West African countries is as shown in Table 2.",
                "Table 2: Daily production of selected West African countries and reserves estimates",
            ],
        )

    def test_preserves_math_components_before_following_prose(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-inline-math.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Glossary</w:t></w:r>
    </w:p>
    <w:p>
      <w:r>
        <m:oMath>
          <m:r><m:t>Densité API=</m:t></m:r>
          <m:f>
            <m:num><m:r><m:t>141,5</m:t></m:r></m:num>
            <m:den><m:r><m:t>Densité à 15°C</m:t></m:r></m:den>
          </m:f>
          <m:r><m:t>-131,5</m:t></m:r>
        </m:oMath>
      </w:r>
      <w:r><w:t>API density</w:t></w:r>
      <w:r><w:t>:</w:t></w:r>
      <w:r><w:t>A scale adopted by the </w:t></w:r>
      <w:r><w:t>American Petroleum Institute (API)</w:t></w:r>
      <w:r><w:t> that evaluates whether oil is light or heavy in relation to water.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_book(docx_path)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "DensitéAPI=141,5/Densitéà15°C-131,5",
                "API density: A scale adopted by the American Petroleum Institute (API) that evaluates whether oil is light or heavy in relation to water.",
            ],
        )

    def test_chapter_anchor_extraction_stops_before_trailing_table_of_contents(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        docx_path = tmp_dir / "fixture-bibliography-tail.docx"
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>Bibliographical References</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>1. IEA (2023): Global Energy Investment Report</w:t></w:r></w:p>
    <w:p><w:r><w:t>2. Alfred Kjemperud (2007): Petroleum contracts</w:t></w:r></w:p>
    <w:p><w:r><w:t>TABLE OF CONTENTS</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
        with zipfile.ZipFile(docx_path, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("_rels/.rels", RELS)
            archive.writestr("word/document.xml", document)
            archive.writestr(
                "word/numbering.xml",
                (FIXTURE_DIR / "numbering-section-restart.xml").read_text(
                    encoding="utf-8"
                ),
            )
            archive.writestr(
                "word/styles.xml",
                (FIXTURE_DIR / "styles-headings.xml").read_text(encoding="utf-8"),
            )

        book = extract_docx_chapter_by_anchors(
            docx_path,
            chapter_title="Bibliographical References",
            start_anchor="1. IEA (2023): Global Energy Investment Report",
        )
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "1. IEA (2023): Global Energy Investment Report",
                "2. Alfred Kjemperud (2007): Petroleum contracts",
            ],
        )


if __name__ == "__main__":
    unittest.main()
