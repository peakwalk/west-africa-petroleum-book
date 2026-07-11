from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
EN_IMAGES = ROOT_DIR / "editions" / "en" / "content" / "images"

FIGURE_TARGETS = (
    {
        "number": 9,
        "asset": "figure-009",
        "chapter": (
            ROOT_DIR
            / "editions"
            / "en"
            / "content"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.md"
        ),
        "source_sha256": "de34cb042c1f3328a5e727b752cb6f861847636c1b86c0009e1d6eab755788eb",
    },
    {
        "number": 41,
        "asset": "figure-041",
        "chapter": (
            ROOT_DIR
            / "editions"
            / "en"
            / "content"
            / "chapters"
            / "chapter-06-upstream-operations-and-government-roles.md"
        ),
        "source_sha256": "216d24d46e3ae41488fbfea767d5f181ccae480bdeddbe4463251f5b53f6882d",
    },
    {
        "number": 69,
        "asset": "figure-069",
        "chapter": (
            ROOT_DIR
            / "editions"
            / "en"
            / "content"
            / "chapters"
            / "chapter-07-petroleum-fiscal-regimes.md"
        ),
        "source_sha256": "b539215fc11f36d6afcd2f2e4200c6164fdf02d2069cb7b2ed02b005be4c57af",
    },
)

ADJACENT_PNG_HASHES = {
    "figure-008": "7202adff6df18888467fc2ec8e149ad669bee044d2283987ca5abc5128dba58c",
    "figure-040": "374d51a3affeac1f40f904fd59f414e463b00687c5e4b5328097c0cbecbef860",
    "figure-068": "2469b456839f3134d18e180ac343f89585df7656c137476f9c8a3e48aa74036a",
}


class Ua19AssetMappingTest(unittest.TestCase):
    def test_reviewed_pngs_use_online_figure_numbers(self) -> None:
        for target in FIGURE_TARGETS:
            with self.subTest(figure=target["number"]):
                png_path = EN_IMAGES / f"{target['asset']}.png"
                digest = hashlib.sha256(png_path.read_bytes()).hexdigest()
                self.assertEqual(digest, target["source_sha256"])

    def test_adjacent_figures_are_not_replaced_by_ua_19_sources(self) -> None:
        for asset_name, expected_digest in ADJACENT_PNG_HASHES.items():
            with self.subTest(asset=asset_name):
                png_path = EN_IMAGES / f"{asset_name}.png"
                digest = hashlib.sha256(png_path.read_bytes()).hexdigest()
                self.assertEqual(digest, expected_digest)

    def test_chapters_reference_reviewed_online_figure_assets(self) -> None:
        for target in FIGURE_TARGETS:
            with self.subTest(figure=target["number"]):
                chapter_text = target["chapter"].read_text(encoding="utf-8")
                self.assertIn(f"../images/{target['asset']}.webp", chapter_text)

    def test_reviewed_webps_are_present_and_nonempty(self) -> None:
        for target in FIGURE_TARGETS:
            with self.subTest(figure=target["number"]):
                webp_path = EN_IMAGES / f"{target['asset']}.webp"
                self.assertGreater(webp_path.stat().st_size, 0)
                self.assertEqual(webp_path.read_bytes()[:4], b"RIFF")


if __name__ == "__main__":
    unittest.main()
