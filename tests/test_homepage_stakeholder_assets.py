from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
HOMEPAGE_CONTENT_PATH = ROOT_DIR / "scripts" / "shared" / "homepage-content.mjs"
STAKEHOLDER_ICON_DIR = ROOT_DIR / "assets" / "icons" / "stakeholders"

EXPECTED_PNG_ASSETS = (
    "governments.png",
    "regulators.png",
    "national-oil-companies.png",
    "operators.png",
    "investors.png",
    "universities-researchers.png",
)


class HomepageStakeholderAssetTests(unittest.TestCase):
    def test_homepage_stakeholder_group_uses_repo_owned_png_assets(self) -> None:
        content = HOMEPAGE_CONTENT_PATH.read_text(encoding="utf-8")

        for asset_name in EXPECTED_PNG_ASSETS:
            self.assertIn(f'assets/icons/stakeholders/{asset_name}"', content)

        self.assertNotIn("assets/icons/stakeholders/governments.svg", content)
        self.assertNotIn("assets/icons/stakeholders/regulators.svg", content)
        self.assertNotIn("assets/icons/stakeholders/national-oil-companies.svg", content)
        self.assertNotIn("assets/icons/stakeholders/operators.svg", content)
        self.assertNotIn("assets/icons/stakeholders/investors.svg", content)
        self.assertNotIn("assets/icons/stakeholders/universities-researchers.svg", content)

    def test_repo_owned_stakeholder_png_assets_exist(self) -> None:
        for asset_name in EXPECTED_PNG_ASSETS:
            self.assertTrue((STAKEHOLDER_ICON_DIR / asset_name).exists(), asset_name)
