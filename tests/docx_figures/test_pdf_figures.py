from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.docx_figures.pdf_figures import (
    PdfCaptionBounds,
    PdfFigurePlacement,
    build_search_windows,
)
from scripts.render_pdf_figures import (
    ensure_lossless_webp_outputs,
    find_cwebp_binary,
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

        self.assertIn("![Figure 017](../images/figure-017.webp)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-017.webp").exists())

    def test_chapter_2_uses_pdf_asset_for_figure_19(self) -> None:
        chapter_text = CHAPTER_02_PATH.read_text(encoding="utf-8")

        self.assertIn("![Figure 019](../images/figure-019.webp)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-019.webp").exists())

    def test_chapter_4_uses_webp_assets_for_selected_pdf_figures(self) -> None:
        chapter_text = (
            ROOT_DIR
            / "src/chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")

        self.assertIn("![Figure 025](../images/figure-025.webp)", chapter_text)
        self.assertIn("![Figure 027](../images/figure-027.webp)", chapter_text)
        self.assertIn("![Figure 028](../images/figure-028.webp)", chapter_text)
        self.assertIn("![Figure 029](../images/figure-029.webp)", chapter_text)
        self.assertIn("![Figure 024](../images/figure-024.webp)", chapter_text)
        self.assertIn("![Figure 031](../images/figure-031.webp)", chapter_text)
        self.assertIn("![Figure 032](../images/figure-032.webp)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-025.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-027.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-028.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-029.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-024.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-031.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-032.webp").exists())

    def test_chapter_3_uses_published_assets_for_selected_figures(self) -> None:
        chapter_text = (
            ROOT_DIR
            / "src/chapters/chapter-03-tax-regimes-in-the-petroleum-sector.md"
        ).read_text(encoding="utf-8")

        self.assertIn("![Figure 021](../images/figure-021.webp)", chapter_text)
        self.assertIn("![Figure 022](../images/figure-022.svg)", chapter_text)
        self.assertIn("![Figure 023](../images/figure-023.webp)", chapter_text)
        self.assertTrue((ROOT_DIR / "src/images/figure-021.webp").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-022.svg").exists())
        self.assertTrue((ROOT_DIR / "src/images/figure-023.webp").exists())

    def test_figure_22_source_asset_is_high_resolution_png(self) -> None:
        output_path = ROOT_DIR / "src/images/figure-022.png"

        self.assertTrue(output_path.exists())

        width, height = _png_dimensions(output_path)
        self.assertGreater(width, 2400)
        self.assertGreater(height, 1400)
        self.assertGreater(output_path.stat().st_size, 500_000)

    def test_figure_22_svg_uses_english_labels(self) -> None:
        svg_text = (ROOT_DIR / "src/images/figure-022.svg").read_text(encoding="utf-8")

        self.assertIn("GOVERNMENT SHARE", svg_text)
        self.assertIn("CONTRACTOR SHARE", svg_text)
        self.assertIn("RECOVERABLE COSTS", svg_text)
        self.assertIn("CONTRACTOR ENTITLEMENT", svg_text)
        self.assertNotIn("PART DU GOUVERNEMENT", svg_text)
        self.assertNotIn("PART DU CONTRACTANT", svg_text)
        self.assertNotIn("COUTS RECUPERABLES", svg_text)

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
            webp_path = output_dir / "figure-024.webp"
            self.assertTrue(output_path.exists(), msg=result.stdout)
            self.assertTrue(webp_path.exists(), msg=result.stdout)

            width, height = _png_dimensions(output_path)
            self.assertGreater(width, 1500)
            self.assertGreater(height, 1000)
            self.assertGreater(output_path.stat().st_size, 100_000)

    def test_find_cwebp_binary_uses_homebrew_fallback(self) -> None:
        with mock.patch("scripts.render_pdf_figures.shutil.which", return_value=None):
            with mock.patch.object(Path, "exists", autospec=True) as exists:
                exists.side_effect = lambda path: str(path) == "/opt/homebrew/bin/cwebp"
                self.assertEqual(find_cwebp_binary(), Path("/opt/homebrew/bin/cwebp"))

    def test_ensure_lossless_webp_outputs_invokes_cwebp(self) -> None:
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
            b"\x1f\x15\xc4\x89"
            b"\x00\x00\x00\rIDATx\x9cc````\xf8\x0f\x00\x01\x04\x01\x00"
            b"\x18\xdd\x8d\xb4"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            png_path = output_dir / "figure-024.png"
            png_path.write_bytes(png_bytes)

            encoder = output_dir / "fake-cwebp"
            encoder.write_text(
                "#!/bin/sh\n"
                "in=\"\"\n"
                "out=\"\"\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  case \"$1\" in\n"
                "    -o)\n"
                "      shift\n"
                "      out=\"$1\"\n"
                "      ;;\n"
                "    -*)\n"
                "      ;;\n"
                "    *)\n"
                "      in=\"$1\"\n"
                "      ;;\n"
                "  esac\n"
                "  shift\n"
                "done\n"
                "cp \"$in\" \"$out\"\n",
                encoding="utf-8",
            )
            encoder.chmod(0o755)

            created = ensure_lossless_webp_outputs(
                output_dir=output_dir,
                figure_numbers=[24],
                cwebp_binary=encoder,
            )

            self.assertEqual(created, [24])
            self.assertTrue((output_dir / "figure-024.webp").exists())

    def test_ensure_lossless_webp_outputs_falls_back_to_sips_when_cwebp_is_missing(self) -> None:
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
            b"\x1f\x15\xc4\x89"
            b"\x00\x00\x00\rIDATx\x9cc````\xf8\x0f\x00\x01\x04\x01\x00"
            b"\x18\xdd\x8d\xb4"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            png_path = output_dir / "figure-024.png"
            png_path.write_bytes(png_bytes)

            sips = output_dir / "fake-sips"
            sips.write_text(
                "#!/bin/sh\n"
                "in=\"\"\n"
                "out=\"\"\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  case \"$1\" in\n"
                "    --out)\n"
                "      shift\n"
                "      out=\"$1\"\n"
                "      ;;\n"
                "    -s)\n"
                "      shift\n"
                "      shift\n"
                "      ;;\n"
                "    *)\n"
                "      in=\"$1\"\n"
                "      ;;\n"
                "  esac\n"
                "  shift\n"
                "done\n"
                "cp \"$in\" \"$out\"\n",
                encoding="utf-8",
            )
            sips.chmod(0o755)

            with mock.patch("scripts.render_pdf_figures.find_cwebp_binary", return_value=None):
                with mock.patch(
                    "scripts.render_pdf_figures.find_sips_binary",
                    return_value=sips,
                ):
                    created = ensure_lossless_webp_outputs(
                        output_dir=output_dir,
                        figure_numbers=[24],
                    )

            self.assertEqual(created, [24])
            self.assertTrue((output_dir / "figure-024.webp").exists())


if __name__ == "__main__":
    unittest.main()
