from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
EN_IMAGES = ROOT_DIR / "editions" / "en" / "content" / "images"
FR_IMAGES = ROOT_DIR / "editions" / "fr" / "content" / "images"
FR_CHAPTER_02 = (
    ROOT_DIR
    / "editions"
    / "fr"
    / "content"
    / "chapters"
    / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
)
FR_CHAPTER_03 = (
    ROOT_DIR
    / "editions"
    / "fr"
    / "content"
    / "chapters"
    / "chapter-03-tax-regimes-in-the-petroleum-sector.md"
)

class FrenchFigureAssetsTest(unittest.TestCase):
    def test_french_published_assets_preserve_french_labels_for_englishized_figures(self) -> None:
        chapter_03 = FR_CHAPTER_03.read_text(encoding="utf-8")
        figure_026 = (FR_IMAGES / "figure-026.svg").read_text(encoding="utf-8")
        figure_030 = (FR_IMAGES / "figure-030.svg").read_text(encoding="utf-8")

        self.assertIn("![Figure 022](../images/figure-022.webp)", chapter_03)
        self.assertNotIn("![Figure 022](../images/figure-022.svg)", chapter_03)
        self.assertFalse((EN_IMAGES / "figure-022.webp").exists())

        self.assertIn("REGIME FISCAL", figure_026)
        self.assertNotIn("FISCAL REGIME", figure_026)

        self.assertIn("REGIME FISCAL", figure_030)
        self.assertNotIn("FISCAL REGIME", figure_030)
        self.assertNotIn("Taxable income: 0", figure_030)

    def test_confirmed_french_source_assets_override_english_bootstrap_fallbacks(self) -> None:
        chapter_02 = FR_CHAPTER_02.read_text(encoding="utf-8")

        self.assertIn("](../images/figure-005.webp)", chapter_02)
        self.assertIn("](../images/figure-006.webp)", chapter_02)
        self.assertIn("![Figure 008](../images/figure-008.webp)", chapter_02)
        self.assertIn("![Figure 009](../images/figure-009.webp)", chapter_02)
        self.assertIn("![Figure 010](../images/figure-010.webp)", chapter_02)
        self.assertIn("![Figure 019](../images/figure-019.webp)", chapter_02)
        self.assertNotIn("figure-005-upstream-phases-transparent.webp", chapter_02)
        self.assertNotIn("figure-006-block-assignment-transparent.webp", chapter_02)
        self.assertNotIn("![Figure 005](../images/figure-005.png)", chapter_02)
        self.assertNotIn("![Figure 006](../images/figure-006.png)", chapter_02)
        self.assertNotIn("![Figure 008](../images/figure-008.png)", chapter_02)
        self.assertNotIn("![Figure 009](../images/figure-009.png)", chapter_02)
        self.assertNotIn("![Figure 009](../images/figure-009.jpg)", chapter_02)
        self.assertNotIn("![Figure 010](../images/figure-010.png)", chapter_02)
        self.assertNotIn("![Figure 019](../images/figure-019.svg)", chapter_02)

        for name in [
            "figure-004.webp",
            "figure-005.webp",
            "figure-006.webp",
            "figure-008.webp",
            "figure-009.webp",
            "figure-010.webp",
            "figure-019.webp",
        ]:
            with self.subTest(name=name):
                self.assertTrue((FR_IMAGES / name).exists())

        self.assertFalse((EN_IMAGES / "figure-008.png").exists())
        self.assertTrue((EN_IMAGES / "figure-009.webp").exists())
        self.assertFalse((FR_IMAGES / "figure-019.svg").exists())

    def test_french_tree_drops_unused_bootstrap_companion_assets(self) -> None:
        for name in [
            "figure-009.jpg",
            "figure-016.webp",
            "figure-017.jpg",
            "figure-017.svg",
            "figure-018.jpg",
            "figure-022.svg",
            "figure-023.svg",
            "figure-026.png",
            "figure-030.png",
            "figures.zip",
        ]:
            with self.subTest(name=name):
                self.assertFalse((FR_IMAGES / name).exists())


if __name__ == "__main__":
    unittest.main()
