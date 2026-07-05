from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class HomepageCountryFlagTests(unittest.TestCase):
    def test_generated_homepage_inlines_country_flag_sprite_for_country_cards(self) -> None:
        with tempfile.TemporaryDirectory(prefix="homepage-country-flags-") as temp_dir:
            output_root = Path(temp_dir)
            subprocess.run(
                ["node", "scripts/generate-index-page.mjs", "--output-root", str(output_root)],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            homepage_html = (output_root / "index.html").read_text(encoding="utf-8")

        self.assertIn('<symbol id="nigeria"', homepage_html)
        self.assertIn('<symbol id="ghana"', homepage_html)
        self.assertIn('<use href="#nigeria"></use>', homepage_html)
        self.assertIn('<use href="#ghana"></use>', homepage_html)
        self.assertNotIn("/assets/icons/country-flags.svg#nigeria", homepage_html)
        self.assertNotIn("/assets/icons/country-flags.svg#ghana", homepage_html)
