from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
EN_IMAGES = ROOT_DIR / "editions" / "en" / "content" / "images"
FR_IMAGES = ROOT_DIR / "editions" / "fr" / "content" / "images"
EN_SOURCE_IMAGES = ROOT_DIR / "editions" / "en" / "source" / "images"
FR_SOURCE_IMAGES = ROOT_DIR / "editions" / "fr" / "source" / "images"

EN_CHAPTER_01 = (
    ROOT_DIR
    / "editions"
    / "en"
    / "content"
    / "chapters"
    / "chapter-01-value-chain-of-the-hydrocarbon-sector.md"
)
EN_CHAPTER_02 = (
    ROOT_DIR
    / "editions"
    / "en"
    / "content"
    / "chapters"
    / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
)
FR_CHAPTER_01 = (
    ROOT_DIR
    / "editions"
    / "fr"
    / "content"
    / "chapters"
    / "chapter-01-value-chain-of-the-hydrocarbon-sector.md"
)
FR_CHAPTER_02 = (
    ROOT_DIR
    / "editions"
    / "fr"
    / "content"
    / "chapters"
    / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
)


def _unreferenced_asset_names(locale: str) -> list[str]:
    chapter_root = ROOT_DIR / "editions" / locale / "content" / "chapters"
    image_root = ROOT_DIR / "editions" / locale / "content" / "images"
    references: set[str] = set()

    for chapter_path in chapter_root.glob("*.md"):
        text = chapter_path.read_text(encoding="utf-8")
        references.update(
            Path(match.group(1)).name
            for match in re.finditer(r"!\[[^\]]*\]\((\.\./images/[^)]+)\)", text)
        )
        references.update(
            Path(match.group(1)).name
            for match in re.finditer(r"""<img[^>]+src=["'](\.\./images/[^"']+)["']""", text)
        )

    return sorted(
        path.name
        for path in image_root.iterdir()
        if path.is_file() and path.name != "figure-manifest.json" and path.name not in references
    )


class FigureReferenceNamesTest(unittest.TestCase):
    def test_english_renamed_figure_references_use_canonical_names(self) -> None:
        chapter_01 = EN_CHAPTER_01.read_text(encoding="utf-8")
        chapter_02 = EN_CHAPTER_02.read_text(encoding="utf-8")

        for expected in [
            "figure-003.webp",
            "figure-004.webp",
            "figure-005.webp",
            "figure-006.webp",
            "figure-009.webp",
            "figure-010.webp",
            "figure-011.webp",
            "figure-012.webp",
            "figure-013.webp",
            "figure-014.webp",
            "figure-015.webp",
            "figure-016-a.webp",
            "figure-016-b.webp",
            "figure-018.webp",
        ]:
            source = chapter_01 if expected in {"figure-003.webp", "figure-004.webp"} else chapter_02
            with self.subTest(expected=expected):
                self.assertIn(expected, source)

        for legacy in [
            "figure-003-map.jpg",
            "figure-004-oil-cuts-transparent.webp",
            "figure-005-upstream-phases-transparent.webp",
            "figure-006-block-assignment-transparent.webp",
            "figure-010-em.webp",
            "figure-011-system.webp",
            "figure-012-geoseismic.webp",
            "figure-013-anticline.webp",
            "figure-014-traps.webp",
            "figure-015-depth-map.webp",
            "figure-018-model.webp",
        ]:
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, chapter_01 + chapter_02)

    def test_french_renamed_figure_references_use_canonical_names(self) -> None:
        chapter_01 = FR_CHAPTER_01.read_text(encoding="utf-8")
        chapter_02 = FR_CHAPTER_02.read_text(encoding="utf-8")

        for expected in [
            "figure-001.webp",
            "figure-003.webp",
            "figure-004.webp",
            "figure-005.webp",
            "figure-006.webp",
            "figure-008.webp",
            "figure-009.webp",
            "figure-010.webp",
            "figure-011.webp",
            "figure-012.webp",
            "figure-013.webp",
            "figure-014.webp",
            "figure-015.webp",
            "figure-016-a.webp",
            "figure-016-b.webp",
            "figure-018.webp",
        ]:
            source = (
                chapter_01
                if expected in {"figure-001.webp", "figure-003.webp", "figure-004.webp"}
                else chapter_02
            )
            with self.subTest(expected=expected):
                self.assertIn(expected, source)

        for legacy in [
            "figure-001-chain.webp",
            "figure-003-map.jpg",
            "figure-010-em.webp",
            "figure-011-system.webp",
            "figure-012-geoseismic.webp",
            "figure-013-anticline.webp",
            "figure-014-traps.webp",
            "figure-015-depth-map.webp",
            "figure-018-model.webp",
        ]:
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, chapter_01 + chapter_02)

    def test_trimmed_and_zip_residual_assets_are_absent(self) -> None:
        expected_absent = [
            EN_IMAGES / "figures.zip",
            EN_IMAGES / "figure-000.png",
            EN_IMAGES / "figure-003-trimmed.png",
            EN_IMAGES / "figure-003-trimmed.webp",
            FR_IMAGES / "figure-000.png",
            FR_IMAGES / "figure-003-trimmed.png",
            FR_IMAGES / "figure-003-trimmed.webp",
            EN_IMAGES / "figure-003.jpg",
            EN_IMAGES / "figure-005.jpg",
            EN_IMAGES / "figure-009.png",
            EN_IMAGES / "figure-009.jpg",
            EN_IMAGES / "figure-010.png",
            EN_IMAGES / "figure-010.jpg",
            EN_IMAGES / "figure-016-a.jpg",
            EN_IMAGES / "figure-016-b.jpg",
            EN_IMAGES / "figure-016.webp",
            EN_IMAGES / "figure-017.jpg",
            EN_IMAGES / "figure-017.svg",
            EN_IMAGES / "figure-018.jpg",
            EN_IMAGES / "figure-019.svg",
            EN_IMAGES / "figure-022.webp",
            EN_IMAGES / "figure-023.svg",
            EN_IMAGES / "figure-007-b.webp",
            EN_IMAGES / "figure-024.svg",
            EN_IMAGES / "figure-025.svg",
            EN_IMAGES / "figure-027.svg",
            EN_IMAGES / "figure-028.svg",
            EN_IMAGES / "figure-029.svg",
            EN_IMAGES / "figure-031.svg",
            EN_IMAGES / "figure-032.svg",
            FR_IMAGES / "figure-002.webp",
            FR_IMAGES / "figure-003.jpg",
            FR_IMAGES / "figure-004.png",
            FR_IMAGES / "figure-005.jpg",
            FR_IMAGES / "figure-005.png",
            FR_IMAGES / "figure-006.png",
            FR_IMAGES / "figure-008.png",
            FR_IMAGES / "figure-009.png",
            FR_IMAGES / "figure-009.jpg",
            FR_IMAGES / "figure-010.png",
            FR_IMAGES / "figure-010.jpg",
            FR_IMAGES / "figure-016-a.jpg",
            FR_IMAGES / "figure-016-b.jpg",
            FR_IMAGES / "figure-016.webp",
            FR_IMAGES / "figure-018.jpg",
            FR_IMAGES / "figure-022.svg",
            FR_IMAGES / "figure-024.svg",
            FR_IMAGES / "figure-025.svg",
            FR_IMAGES / "figure-027.svg",
            FR_IMAGES / "figure-028.svg",
            FR_IMAGES / "figure-029.svg",
            FR_IMAGES / "figure-031.svg",
            FR_IMAGES / "figure-032.svg",
        ]

        for path in expected_absent:
            with self.subTest(path=path.name):
                self.assertFalse(path.exists(), f"Expected residual asset to be deleted: {path}")

    def test_cover_source_pngs_live_outside_published_images(self) -> None:
        self.assertTrue((EN_SOURCE_IMAGES / "figure-000.png").exists())
        self.assertTrue((FR_SOURCE_IMAGES / "figure-000.png").exists())

    def test_no_unreferenced_assets_remain_in_published_image_roots(self) -> None:
        self.assertEqual(_unreferenced_asset_names("en"), [])
        self.assertEqual(_unreferenced_asset_names("fr"), [])


if __name__ == "__main__":
    unittest.main()
