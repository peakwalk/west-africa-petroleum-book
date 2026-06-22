from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
REPLACEMENT_DOCX_PATH = (
    ROOT_DIR / "resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx"
)
RENDER_SCRIPT = ROOT_DIR / "scripts/render_docx_bitmap_figures.py"
SUMMARY_PATH = ROOT_DIR / "editions/en/content/SUMMARY.md"
CHAPTERS_DIR = ROOT_DIR / "editions/en/content/chapters"


class BitmapMediaTest(unittest.TestCase):
    def test_render_replacement_english_docx_bitmap_figure_80(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = subprocess.run(
                [
                    sys.executable,
                    str(RENDER_SCRIPT),
                    "--docx",
                    str(REPLACEMENT_DOCX_PATH),
                    "--summary",
                    str(SUMMARY_PATH),
                    "--chapters-dir",
                    str(CHAPTERS_DIR),
                    "--figures",
                    "80",
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
            self.assertTrue((output_dir / "figure-080.png").exists(), msg=result.stdout)
            self.assertTrue((output_dir / "figure-080.webp").exists(), msg=result.stdout)


if __name__ == "__main__":
    unittest.main()
