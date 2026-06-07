from __future__ import annotations

import json
import unittest

from scripts.docx_figures.model import FigureCoverageDiff
from scripts.docx_figures.report import (
    render_figure_coverage_json,
    render_figure_coverage_text,
)


class FigureReportTest(unittest.TestCase):
    def test_render_text_report_lists_each_diff(self) -> None:
        report = render_figure_coverage_text(
            [
                FigureCoverageDiff(
                    figure_number=24,
                    chapter_path="chapter-04.md",
                    diff_type="markdown.missing_image_reference",
                    detail="No Markdown reference.",
                )
            ]
        )
        self.assertIn("Figure 24 [markdown.missing_image_reference]", report)
        self.assertIn("chapter: chapter-04.md", report)

    def test_render_json_report_is_machine_readable(self) -> None:
        payload = json.loads(
            render_figure_coverage_json(
                [
                    FigureCoverageDiff(
                        figure_number=31,
                        chapter_path="chapter-04.md",
                        diff_type="assets.missing_file",
                        detail="Missing SVG asset.",
                    )
                ]
            )
        )
        self.assertEqual(payload[0]["figure_number"], 31)
        self.assertEqual(payload[0]["diff_type"], "assets.missing_file")


if __name__ == "__main__":
    unittest.main()
