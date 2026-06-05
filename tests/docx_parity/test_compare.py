import unittest

from scripts.docx_parity.compare import compare_books
from scripts.docx_parity.model import (
    BodyBlock,
    BookSemanticModel,
    ChapterSemanticModel,
    OutlineEntry,
)
from scripts.docx_parity.report import render_text_report


class CompareBooksTests(unittest.TestCase):
    def test_reports_outline_number_mismatch(self) -> None:
        docx_book = BookSemanticModel(
            chapters=[
                ChapterSemanticModel(
                    source_path="docx:chapter-1",
                    title="Chapter 1: Value Chain of the Hydrocarbon Sector",
                    outline=[
                        OutlineEntry(
                            level=2,
                            number="1.1-",
                            title="The Upstream segment",
                        )
                    ],
                    body=[BodyBlock(kind="paragraph", text="Intro paragraph.")],
                )
            ]
        )
        markdown_book = BookSemanticModel(
            chapters=[
                ChapterSemanticModel(
                    source_path=(
                        "src/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.md"
                    ),
                    title="Chapter 1: Value Chain of the Hydrocarbon Sector",
                    outline=[
                        OutlineEntry(level=2, number="1.", title="The Upstream segment")
                    ],
                    body=[BodyBlock(kind="paragraph", text="Intro paragraph.")],
                )
            ]
        )

        diffs = compare_books(docx_book, markdown_book)

        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0].diff_type, "outline.number_mismatch")
        self.assertIn(
            "Promote this item to a real section heading", render_text_report(diffs)
        )


if __name__ == "__main__":
    unittest.main()
