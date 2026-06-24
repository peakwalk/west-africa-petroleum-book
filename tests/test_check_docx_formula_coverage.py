from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.docx_parity.model import BodyBlock, BookSemanticModel, ChapterSemanticModel

from scripts.check_docx_formula_coverage import (
    FormulaCoverageDiff,
    find_formula_coverage_diffs,
    is_formula_candidate,
)


class CheckDocxFormulaCoverageTests(unittest.TestCase):
    def test_is_formula_candidate_matches_equations_but_not_explanatory_sentences(self) -> None:
        self.assertTrue(
            is_formula_candidate("Post-Royalty Revenue = Gross Revenue - Royalty")
        )
        self.assertTrue(
            is_formula_candidate("100-(32.5xH) to 100-(47.5xH) for the State")
        )
        self.assertTrue(is_formula_candidate("= 0.55 (55%)"))
        self.assertFalse(
            is_formula_candidate(
                "FVF (Formation Volume Factor) - expresses the change in fluid volume "
                "between reservoir conditions and standard surface conditions "
                "(pressure = 1 atmosphere and temperature = 15°C)."
            )
        )
        self.assertFalse(is_formula_candidate("GIIP (Gas Initially In Place)"))
        self.assertFalse(is_formula_candidate("BBL/D/1K : One Thousand Barrels Per Day"))

    def test_find_formula_coverage_diffs_ignores_rendered_formula_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chapter_path = Path(tmpdir) / "chapter-08-test.md"
            chapter_path.write_text(
                "# Chapter 8: Test\n\n"
                '<div class="book-formula" role="img" aria-label="Post royalty revenue">\n'
                '  <span class="book-formula-line" aria-hidden="true">'
                "Post-Royalty Revenue = Gross Revenue &minus; Royalty"
                "</span>\n"
                "</div>\n",
                encoding="utf-8",
            )

            docx_book = BookSemanticModel(
                chapters=[
                    ChapterSemanticModel(
                        source_path=str(chapter_path),
                        title="Test",
                        body=[
                            BodyBlock(
                                kind="paragraph",
                                text="Post-Royalty Revenue = Gross Revenue - Royalty",
                            )
                        ],
                    )
                ]
            )

            self.assertEqual(find_formula_coverage_diffs(docx_book), [])

    def test_find_formula_coverage_diffs_reports_missing_formula_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chapter_path = Path(tmpdir) / "chapter-08-test.md"
            chapter_path.write_text(
                "# Chapter 8: Test\n\n"
                "This chapter has no semantic formula block.\n",
                encoding="utf-8",
            )

            docx_book = BookSemanticModel(
                chapters=[
                    ChapterSemanticModel(
                        source_path=str(chapter_path),
                        title="Test",
                        body=[
                            BodyBlock(
                                kind="paragraph",
                                text="Post-Royalty Revenue = Gross Revenue - Royalty",
                            )
                        ],
                    )
                ]
            )

            self.assertEqual(
                find_formula_coverage_diffs(docx_book),
                [
                    FormulaCoverageDiff(
                        chapter_path=str(chapter_path),
                        docx_value="Post-Royalty Revenue = Gross Revenue - Royalty",
                    )
                ],
            )


if __name__ == "__main__":
    unittest.main()
