from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.docx_figures.pdf_figures import (
    PdfCaptionBounds,
    PdfFigurePlacement,
    build_search_windows,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
PDF_PATH = ROOT_DIR / "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf"
RENDER_SCRIPT = ROOT_DIR / "scripts/render_pdf_figures.py"
CHAPTER_02_PATH = (
    ROOT_DIR
    / "src/chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
)


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError(f"{path} is not a PNG file")
    return struct.unpack(">II", data[16:24])


class PdfFiguresTest(unittest.TestCase):
    def test_chapter_2_uses_pdf_asset_for_figure_17(self) -> None:
        chapter_text = CHAPTER_02_PATH.read_text(encoding="utf-8")

        self.assertIn("![Figure 017](../images/figure-017.png)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-017.png").exists())

    def test_chapter_2_uses_pdf_asset_for_figure_19(self) -> None:
        chapter_text = CHAPTER_02_PATH.read_text(encoding="utf-8")

        self.assertIn("![Figure 019](../images/figure-019.png)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-019.png").exists())

    def test_chapter_3_uses_pdf_asset_for_figure_21(self) -> None:
        chapter_text = (
            ROOT_DIR
            / "src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md"
        ).read_text(encoding="utf-8")

        self.assertIn("![Figure 021](../images/figure-021.png)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-021.png").exists())

    def test_figure_22_source_asset_is_high_resolution_png(self) -> None:
        output_path = ROOT_DIR / "src/images/figure-022.png"

        self.assertTrue(output_path.exists())

        width, height = _png_dimensions(output_path)
        self.assertGreater(width, 2400)
        self.assertGreater(height, 1400)
        self.assertGreater(output_path.stat().st_size, 500_000)

    def test_build_search_windows_separates_multiple_figures_on_the_same_page(self) -> None:
        placements = [
            PdfFigurePlacement(
                figure_number=31,
                page_number=97,
                caption_bounds=PdfCaptionBounds(
                    x=70.80,
                    y=513.67,
                    width=57.99,
                    height=15.48,
                    page_width=595.20,
                    page_height=841.92,
                ),
            ),
            PdfFigurePlacement(
                figure_number=32,
                page_number=97,
                caption_bounds=PdfCaptionBounds(
                    x=70.80,
                    y=235.99,
                    width=57.77,
                    height=15.48,
                    page_width=595.20,
                    page_height=841.92,
                ),
            ),
        ]

        windows = {
            window.figure_number: window
            for window in build_search_windows(placements)
        }

        self.assertAlmostEqual(windows[31].top, 801.92, places=2)
        self.assertAlmostEqual(windows[31].bottom, 539.15, places=2)
        self.assertAlmostEqual(windows[32].top, 501.67, places=2)
        self.assertAlmostEqual(windows[32].bottom, 261.47, places=2)
        self.assertLess(windows[32].top, windows[31].bottom)

    def test_render_pdf_figure_24_creates_high_resolution_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = subprocess.run(
                [
                    sys.executable,
                    str(RENDER_SCRIPT),
                    "--pdf",
                    str(PDF_PATH),
                    "--figures",
                    "24",
                    "--output-dir",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=str(ROOT_DIR),
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )

            output_path = output_dir / "figure-024.png"
            self.assertTrue(output_path.exists(), msg=result.stdout)

            width, height = _png_dimensions(output_path)
            self.assertGreater(width, 1500)
            self.assertGreater(height, 1000)
            self.assertGreater(output_path.stat().st_size, 100_000)


if __name__ == "__main__":
    unittest.main()
