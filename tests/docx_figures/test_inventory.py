from __future__ import annotations

import unittest
from pathlib import Path
import tempfile

from scripts.docx_figures.inventory import (
    _published_asset_candidates,
    build_figure_inventory,
    classify_figure,
)
from scripts.docx_figures.model import FigureObjectStats

ROOT_DIR = Path(__file__).resolve().parents[2]
REPLACEMENT_DOCX_PATH = (
    ROOT_DIR / "resources/Exploration et exploitation des ressources pétrolières en Afrique de 1 (EN).docx"
)
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

    def test_replacement_english_docx_inventory_uses_existing_canonical_asset_prefixes(self) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=REPLACEMENT_DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }

        self.assertEqual(inventory[1].published_assets, ["figure-001.webp"])
        self.assertEqual(inventory[2].published_assets, ["figure-002.webp"])

    def test_published_asset_candidates_prefer_webp_over_png_with_same_figure_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            images_dir = Path(tmpdir)
            (images_dir / "figure-001.png").write_bytes(b"png")
            (images_dir / "figure-001.webp").write_bytes(b"webp")
            (images_dir / "figure-002-a.png").write_bytes(b"png-a")
            (images_dir / "figure-002-a.webp").write_bytes(b"webp-a")
            (images_dir / "figure-002-b.png").write_bytes(b"png-b")

            self.assertEqual(_published_asset_candidates(images_dir, 1), ["figure-001.webp"])
            self.assertEqual(
                _published_asset_candidates(images_dir, 2),
                ["figure-002-a.webp", "figure-002-b.png"],
            )

    def test_published_asset_candidates_skip_empty_webp_and_fallback_to_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            images_dir = Path(tmpdir)
            (images_dir / "figure-011.png").write_bytes(b"png")
            (images_dir / "figure-011.webp").write_bytes(b"")

            self.assertEqual(_published_asset_candidates(images_dir, 11), ["figure-011.png"])

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

    def test_replacement_english_docx_inventory_covers_figures_1_through_80(self) -> None:
        inventory = build_figure_inventory(
            docx_path=REPLACEMENT_DOCX_PATH,
            chapters_dir=CHAPTERS_DIR,
            summary_path=SUMMARY_PATH,
        )

        self.assertEqual([record.number for record in inventory], list(range(1, 81)))

    def test_replacement_english_docx_inventory_uses_replacement_chapter_paths(self) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=REPLACEMENT_DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }

        self.assertEqual(
            inventory[5].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md"
                ).resolve()
            ),
        )
        self.assertEqual(
            inventory[80].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/en/content/chapters/chapter-12-vision-for-west-africa-2050.md"
                ).resolve()
            ),
        )

    def test_replacement_english_docx_inventory_does_not_treat_body_chapter_mentions_as_headings(
        self,
    ) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=REPLACEMENT_DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }

        self.assertEqual(
            inventory[1].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/en/content/chapters/chapter-01-general-introduction.md"
                ).resolve()
            ),
        )
        self.assertEqual(
            inventory[2].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/en/content/chapters/chapter-01-general-introduction.md"
                ).resolve()
            ),
        )
        self.assertEqual(
            inventory[3].chapter_path,
            str(
                (
                    ROOT_DIR
                    / "editions/en/content/chapters/chapter-01-general-introduction.md"
                ).resolve()
            ),
        )
        self.assertEqual(
            inventory[1].caption,
            "Figure 1: African Petroleum Development Paradox. Resource wealth does not "
            "automatically translate into broad-based economic development.",
        )

    def test_replacement_english_docx_inventory_prefers_caption_paragraphs_over_body_mentions(
        self,
    ) -> None:
        inventory = {
            record.number: record
            for record in build_figure_inventory(
                docx_path=REPLACEMENT_DOCX_PATH,
                chapters_dir=CHAPTERS_DIR,
                summary_path=SUMMARY_PATH,
            )
        }

        self.assertEqual(
            inventory[69].caption,
            "Figure 69: Illustration of how production revenues are allocated between "
            "cost recovery, contractor entitlement, and government take under a "
            "typical petroleum fiscal regime.",
        )
        self.assertEqual(
            inventory[70].caption,
            "Figure 70: Overview of the principal petroleum fiscal regimes used "
            "worldwide, including concessionary systems, service contracts, and "
            "production sharing contracts, together with examples of countries "
            "where they are applied.",
        )


if __name__ == "__main__":
    unittest.main()
