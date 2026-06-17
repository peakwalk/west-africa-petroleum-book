from __future__ import annotations

import unittest
from pathlib import Path

from scripts.docx_figures.inventory import build_figure_inventory
from scripts.docx_figures.vector_media import render_vector_blip_png

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCX_PATH = ROOT_DIR / "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
SUMMARY_PATH = ROOT_DIR / "editions/en/content/SUMMARY.md"
CHAPTERS_DIR = ROOT_DIR / "editions/en/content/chapters"


class VectorMediaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = {
            record.number: record
            for record in build_figure_inventory(DOCX_PATH, CHAPTERS_DIR, SUMMARY_PATH)
        }

    def test_render_figure_22_emits_png_bytes(self) -> None:
        record = self.inventory[22]

        width, height, png_bytes = render_vector_blip_png(
            DOCX_PATH,
            record.objects.blip_targets[0],
        )

        self.assertGreater(width, 2500)
        self.assertGreater(height, 1500)
        self.assertTrue(png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertGreater(len(png_bytes), 100_000)


if __name__ == "__main__":
    unittest.main()
