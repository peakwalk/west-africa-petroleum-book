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
        chapter_path.write_text(
            (FIXTURE_DIR / "chapter-minimal.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 1: Value Chain of the Hydrocarbon Sector]"
            "(chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            chapter.title, "Chapter 1: Value Chain of the Hydrocarbon Sector"
        )
        self.assertEqual(chapter.outline[0].number, "1.1-")
        self.assertEqual(chapter.outline[1].number, "1.1.1-")
        self.assertEqual(
            [block.text for block in chapter.body],
            ["Intro paragraph.", "Figure 1: Oil Sector Value Chain"],
        )

    def test_merges_wrapped_list_items_and_ignores_pre_heading_figure_labels(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-02-different-phases.md"
        chapter_path.write_text(
            "# Chapter 2: Different Phases of Upstream Oil and the Roles of States\n\n"
            "Intro paragraph.\n\n"
            "Figure 5: Different phases of upstream oil\n\n"
            "Authorization to operate\n\n"
            "Exploration Authorization\n\n"
            "## 2.1- *Pre-licensing phase*\n\n"
            "A body paragraph.\n\n"
            "- Research or exploration: the identification of hydrocarbon\n"
            "  accumulations by various geological and geophysical methods.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 2: Different Phases of Upstream Oil and the Roles of States]"
            "(chapters/chapter-02-different-phases.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph", "list_item"],
        )
        self.assertEqual(
            chapter.body[-1].text,
            "Research or exploration: the identification of hydrocarbon accumulations by various geological and geophysical methods.",
        )

    def test_ignores_markdown_tables_and_unescapes_table_sources(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-03-value-chain.md"
        chapter_path.write_text(
            "# Chapter 3: Tables and Captions\n\n"
            "## 3.1- *State of play*\n\n"
            "Paragraph before the table.\n\n"
            "| Country | Value |\n"
            "|:--|:--|\n"
            "| Benin | 331 |\n"
            "| Ghana | 1813 |\n\n"
            "Table 1: Estimation of\n"
            "hydrocarbon resources in West Africa\n\n"
            "\\*Data Ministries\n\n"
            "\\*\\*RPS Energy Report, 2006\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 3: Tables and Captions](chapters/chapter-03-value-chain.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Paragraph before the table.",
                "Table 1: Estimation of hydrocarbon resources in West Africa",
                "Data Ministries",
                "RPS Energy Report, 2006",
            ],
        )

    def test_strips_html_superscript_markers_from_table_sources(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-03-value-chain.md"
        chapter_path.write_text(
            "# Chapter 3: Tables and Captions\n\n"
            "## 3.1- *State of play*\n\n"
            "Paragraph before the table.\n\n"
            "| Country | Value |\n"
            "|:--|:--|\n"
            "| Benin | 331<sup>1</sup> |\n\n"
            "Table 1: Estimation of hydrocarbon resources in West Africa\n\n"
            "<sup>1</sup> Data Ministries\n\n"
            "<sup>2</sup> RPS Energy Report, 2006\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 3: Tables and Captions](chapters/chapter-03-value-chain.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Paragraph before the table.",
                "Table 1: Estimation of hydrocarbon resources in West Africa",
                "Data Ministries",
                "RPS Energy Report, 2006",
            ],
        )

    def test_ignores_html_tables_and_inline_figure_labels(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-04-figures.md"
        chapter_path.write_text(
            "# Chapter 4: Figures and Tables\n\n"
            "## 4.1- *Exploration*\n\n"
            "Table 3: Type of crude oil in selected West African countries\n\n"
            "<table>\n"
            "<tr><td>Benin</td><td>331</td></tr>\n"
            "</table>\n\n"
            "Lead-in paragraph.\n\n"
            "b\n\n"
            "![Figure 008](../images/figure-008.webp)\n\n"
            "a\n\n"
            "Multiple qv streamers\n\n"
            "![Figure 009](../images/figure-009.webp)\n\n"
            "Source\n\n"
            "Figure 8: 3D acquisition\n"
            "principle (a) and seismic cube (b)\n\n"
            "Exploratory drilling is the ultimate and very expensive step.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 4: Figures and Tables](chapters/chapter-04-figures.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["caption", "paragraph", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Table 3: Type of crude oil in selected West African countries",
                "Lead-in paragraph.",
                "Figure 8: 3D acquisition principle (a) and seismic cube (b)",
                "Exploratory drilling is the ultimate and very expensive step.",
            ],
        )

    def test_preserves_emphasized_semantic_callout_before_figure(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-05-callouts.md"
        chapter_path.write_text(
            "# Chapter 5: Development\n\n"
            "## 5.1- *Development phase*\n\n"
            "CAPEX, OPEX, Risk\n\n"
            "**ECONOMIC EVALUATION AND DECISIONS**\n\n"
            "Figure 17: Methodology\n"
            "Tank Evaluation\n\n"
            "![Figure 019](../images/figure-019.webp)\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 5: Development](chapters/chapter-05-callouts.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "paragraph", "caption"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "CAPEX, OPEX, Risk",
                "ECONOMIC EVALUATION AND DECISIONS",
                "Figure 17: Methodology Tank Evaluation",
            ],
        )

    def test_extracts_html_table_caption_while_ignoring_table_cells(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-07-html-table-caption.md"
        chapter_path.write_text(
            "# Chapter 7: Measurement\n\n"
            "## 7.1- *Metering*\n\n"
            "Lead-in paragraph.\n\n"
            "<table>\n"
            "<caption><p>Table 4:\n"
            "Calculation of the financial losses that would result from a measurement\n"
            "error of 0.4%</p></caption>\n"
            "<tr><td>Benin</td><td>1</td></tr>\n"
            "</table>\n\n"
            "Closing paragraph.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 7: Measurement](chapters/chapter-07-html-table-caption.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "Table 4: Calculation of the financial losses that would result from a measurement error of 0.4%",
                "Closing paragraph.",
            ],
        )

    def test_extracts_french_html_table_caption_while_ignoring_table_cells(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-07-french-html-table-caption.md"
        chapter_path.write_text(
            "# Chapitre 7 : Mesure\n\n"
            "## 7.1- *Comptage*\n\n"
            "Paragraphe d’introduction.\n\n"
            "<table>\n"
            "<caption><p>Tableau 4:\n"
            "Calcul des pertes financières qui résulteraient d’une erreur de mesure\n"
            "de 0,4 %</p></caption>\n"
            "<tr><td>Bénin</td><td>1</td></tr>\n"
            "</table>\n\n"
            "Paragraphe de clôture.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapitre 7 : Mesure](chapters/chapter-07-french-html-table-caption.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "caption", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Paragraphe d’introduction.",
                "Tableau 4: Calcul des pertes financières qui résulteraient d’une erreur de mesure de 0,4 %",
                "Paragraphe de clôture.",
            ],
        )

    def test_normalizes_html_formula_blocks_and_ignores_formula_bridge(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-08-formulas.md"
        chapter_path.write_text(
            "# Chapter 8: Formula Blocks\n\n"
            "## 8.1- *Tax formulas*\n\n"
            "Lead-in paragraph.\n\n"
            '<div class="book-formula" role="img" aria-label="Post royalty revenue equals gross revenue minus royalty">\n'
            '  <span class="book-formula-line" aria-hidden="true">Post Royalty Revenue = Gross Revenue &minus; Royalty</span>\n'
            "</div>\n\n"
            '<p class="book-formula-bridge">or</p>\n\n'
            '<div class="book-formula" role="img" aria-label="Oil profit equals gross revenue minus royalty minus recoverable costs">\n'
            '  <span class="book-formula-line" aria-hidden="true">Oil Profit = Gross Revenue &minus; Royalty &minus; Recoverable Costs</span>\n'
            "</div>\n\n"
            "Closing paragraph.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 8: Formula Blocks](chapters/chapter-08-formulas.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "paragraph", "paragraph", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "Post Royalty Revenue = Gross Revenue - Royalty or",
                "Oil Profit = Gross Revenue - Royalty - Recoverable Costs",
                "Closing paragraph.",
            ],
        )

    def test_extracts_formula_notes_as_assessment_paragraphs(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-08-formula-notes.md"
        chapter_path.write_text(
            "# Chapter 8: Formula Blocks\n\n"
            "## 8.1- *Prospect formulas*\n\n"
            "Lead-in paragraph.\n\n"
            '<div class="book-formula" role="img" aria-label="P prospect equals P source rock times P reservoir times P trap">\n'
            '  <span class="book-formula-line" aria-hidden="true">P(prospect) = P(source rock) x P(reservoir) x P(trap)</span>\n'
            "</div>\n\n"
            '<div class="formula-notes" aria-label="Prospect formula notes">\n'
            '  <p class="formula-note"><span class="formula-note-term">P(prospect):</span> Geological hazards</p>\n'
            '  <p class="formula-note"><span class="formula-note-term">P(source rock):</span> Maturity of the bedrock and therefore its degree of migration to the reservoir</p>\n'
            "</div>\n\n"
            "Closing paragraph.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 8: Formula Blocks](chapters/chapter-08-formula-notes.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.kind for block in chapter.body],
            ["paragraph", "paragraph", "paragraph", "paragraph", "paragraph"],
        )
        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Lead-in paragraph.",
                "P(prospect) = P(source rock) x P(reservoir) x P(trap)",
                "P(prospect): Geological hazards",
                "P(source rock): Maturity of the bedrock and therefore its degree of migration to the reservoir",
                "Closing paragraph.",
            ],
        )

    def test_unescapes_currency_markdown_escapes_in_paragraphs(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-06-currency.md"
        chapter_path.write_text(
            "# Chapter 6: Economics\n\n"
            "## 6.1- *Sensitivity*\n\n"
            "The economic model was based on crude oil priced at \\$80, later falling from \\$110 to \\$36.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n"
            "- [Chapter 6: Economics](chapters/chapter-06-currency.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "The economic model was based on crude oil priced at $80, later falling from $110 to $36.",
            ],
        )

    def test_normalizes_fenced_math_blocks_into_paragraphs(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-08-glossary.md"
        chapter_path.write_text(
            "# Glossary\n\n"
            "**DHI:** Intro text.\n\n"
            "``` math\n"
            "\\mathbf{Densité\\ API =}\\frac{\\mathbf{141,5}}{\\mathbf{Densité\\ à\\ 15{^\\circ}C}}\\mathbf{- 131,5}\n"
            "```\n\n"
            "**API density**: A scale adopted by the American Petroleum Institute.\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n- [Glossary](chapters/chapter-08-glossary.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "DHI: Intro text.",
                "DensitéAPI=141,5/Densitéà15°C-131,5",
                "API density: A scale adopted by the American Petroleum Institute.",
            ],
        )

    def test_unescapes_angle_bracket_markdown_escapes_in_lists(self) -> None:
        tmp_dir = Path(tempfile.mkdtemp())
        chapter_dir = tmp_dir / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_path = chapter_dir / "chapter-09-api.md"
        chapter_path.write_text(
            "# Glossary\n\n"
            "- Light oil (API \\> 30°)\n"
            "- Extra-heavy oil (API \\< 10°)\n",
            encoding="utf-8",
        )
        summary_path = tmp_dir / "SUMMARY.md"
        summary_path.write_text(
            "# Summary\n\n- [Glossary](chapters/chapter-09-api.md)\n",
            encoding="utf-8",
        )

        book = extract_markdown_book(summary_path, chapter_dir)
        chapter = book.chapters[0]

        self.assertEqual(
            [block.text for block in chapter.body],
            [
                "Light oil (API > 30°)",
                "Extra-heavy oil (API < 10°)",
            ],
        )


if __name__ == "__main__":
    unittest.main()
