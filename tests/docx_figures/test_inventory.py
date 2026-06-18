from __future__ import annotations

import unittest
from pathlib import Path

from scripts.docx_figures.inventory import build_figure_inventory, classify_figure
from scripts.docx_figures.model import FigureObjectStats

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCX_PATH = ROOT_DIR / "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
SUMMARY_PATH = ROOT_DIR / "editions/en/content/SUMMARY.md"
CHAPTERS_DIR = ROOT_DIR / "editions/en/content/chapters"
FR_DOCX_PATH = ROOT_DIR / "resources/editions/fr/reference.docx"
FR_SUMMARY_PATH = ROOT_DIR / "editions/fr/content/SUMMARY.md"
FR_CHAPTERS_DIR = ROOT_DIR / "editions/fr/content/chapters"


class InventoryTest(unittest.TestCase):
    def test_classify_chart_shape_and_vector_variants(self) -> None:
        self.assertEqual(
            classify_figure(FigureObjectStats(chart_targets=["word/charts/chart1.xml"])),
            "chart",
        )
        self.assertEqual(
            classify_figure(FigureObjectStats(vshape_count=3, wps_shape_count=3)),
            "shape_group",
        )
        self.assertEqual(
            classify_figure(FigureObjectStats(blip_targets=["word/media/image3.wmf"])),
            "vector_media",
        )
        self.assertEqual(
            classify_figure(
                FigureObjectStats(blip_targets=["word/media/image1.png", "word/media/image2.png"])
            ),
            "multi_photo",
        )

    def test_live_docx_inventory_covers_figures_1_through_32(self) -> None:
        inventory = build_figure_inventory(
            docx_path=DOCX_PATH,
            chapters_dir=CHAPTERS_DIR,
            summary_path=SUMMARY_PATH,
        )
        self.assertEqual([record.number for record in inventory], list(range(1, 33)))

    def test_live_docx_inventory_classifies_late_figures(self) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }
        self.assertEqual(inventory[24].kind, "chart")
        self.assertIn(inventory[25].kind, {"shape_group", "composite"})
        self.assertEqual(inventory[31].kind, "chart")
        self.assertEqual(inventory[32].kind, "chart")

    def test_english_docx_inventory_uses_canonical_figure_one_asset_names(self) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }

        self.assertEqual(inventory[1].published_assets, ["figure-001.webp"])
        self.assertEqual(inventory[2].published_assets, ["figure-002-a.webp", "figure-002-b.webp"])

    def test_french_docx_inventory_covers_figures_1_through_32(self) -> None:
        inventory = build_figure_inventory(
            docx_path=FR_DOCX_PATH,
            chapters_dir=FR_CHAPTERS_DIR,
            summary_path=FR_SUMMARY_PATH,
        )

        self.assertEqual([record.number for record in inventory], list(range(1, 33)))

    def test_french_docx_inventory_uses_french_figure_index_chapter_targets(self) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=FR_DOCX_PATH,
                chapters_dir=FR_CHAPTERS_DIR,
                summary_path=FR_SUMMARY_PATH,
            )
        }

        self.assertEqual(
            inventory[5].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/fr/content"
                    / "chapters"
                    / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
                ).resolve()
            ),
        )


if __name__ == "__main__":
    unittest.main()
