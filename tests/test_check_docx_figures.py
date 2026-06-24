from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_docx_figures import _coverage_diffs
from scripts.docx_figures.model import FigureObjectStats, FigureRecord


class CheckDocxFiguresTest(unittest.TestCase):
    def test_coverage_diffs_reports_empty_markdown_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            chapters_dir = root / "chapters"
            chapters_dir.mkdir()
            chapter_path = chapters_dir / "chapter-05.md"
            chapter_path.write_text("placeholder", encoding="utf-8")
            images_dir = root / "images"
            images_dir.mkdir()
            (images_dir / "figure-011.webp").write_bytes(b"")

            record = FigureRecord(
                number=11,
                caption="Figure 11: Example",
                chapter_title="Chapter 5: Hydrocarbon Value Chain",
                chapter_path=str(chapter_path),
                caption_paragraph_index=1,
                object_paragraph_start=0,
                object_paragraph_end=1,
                kind="bitmap",
                objects=FigureObjectStats(blip_targets=["word/media/image11.png"]),
                published_assets=["figure-011.webp"],
            )

            diffs = _coverage_diffs(
                records=[record],
                markdown_refs={11: [(str(chapter_path), "../images/figure-011.webp")]},
                images_root=images_dir,
            )

            self.assertTrue(
                any(diff.diff_type == "assets.empty_file" for diff in diffs),
                "Expected empty Markdown figure targets to be reported.",
            )

    def test_coverage_diffs_reports_empty_manifest_selected_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            chapters_dir = root / "chapters"
            chapters_dir.mkdir()
            chapter_path = chapters_dir / "chapter-05.md"
            chapter_path.write_text("placeholder", encoding="utf-8")
            images_dir = root / "images"
            images_dir.mkdir()
            (images_dir / "figure-011.webp").write_bytes(b"")
            (images_dir / "figure-011.png").write_bytes(b"png")

            record = FigureRecord(
                number=11,
                caption="Figure 11: Example",
                chapter_title="Chapter 5: Hydrocarbon Value Chain",
                chapter_path=str(chapter_path),
                caption_paragraph_index=1,
                object_paragraph_start=0,
                object_paragraph_end=1,
                kind="bitmap",
                objects=FigureObjectStats(blip_targets=["word/media/image11.png"]),
                published_assets=["figure-011.webp"],
            )

            diffs = _coverage_diffs(
                records=[record],
                markdown_refs={11: [(str(chapter_path), "../images/figure-011.png")]},
                images_root=images_dir,
            )

            self.assertTrue(
                any(diff.diff_type == "manifest.empty_file" for diff in diffs),
                "Expected empty manifest-selected figure assets to be reported.",
            )


if __name__ == "__main__":
    unittest.main()
