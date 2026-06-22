from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "editions.json"


class PublicEditionBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp_dir = Path(tempfile.mkdtemp(prefix="public-editions-test-"))
        cls.output_root = cls._temp_dir / "output"

        subprocess.run(
            ["node", "scripts/generate-index-page.mjs", "--output-root", str(cls.output_root)],
            cwd=ROOT_DIR,
            check=True,
        )
        subprocess.run(
            ["node", "scripts/generate-legal-pages.mjs", "--output-root", str(cls.output_root)],
            cwd=ROOT_DIR,
            check=True,
        )
        subprocess.run(
            ["node", "scripts/generate-chapters-page.mjs", "--output-root", str(cls.output_root)],
            cwd=ROOT_DIR,
            check=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        subprocess.run(["rm", "-rf", str(cls._temp_dir)], check=True)

    def test_shared_registry_declares_english_and_french_editions(self) -> None:
        registry = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(["en", "fr"], [edition["locale"] for edition in registry["editions"]])

    def test_shared_registry_declares_locale_scoped_figure_roots(self) -> None:
        registry = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        editions = {edition["locale"]: edition for edition in registry["editions"]}

        self.assertEqual("editions/en", editions["en"]["editionRoot"])
        self.assertEqual(
            "scripts/docx_figures/figure_text_englishization_map.json",
            editions["en"]["figureTextReplacementMapPath"],
        )

        self.assertEqual("editions/fr", editions["fr"]["editionRoot"])
        self.assertTrue(
            "figureTextReplacementMapPath" not in editions["fr"]
            or editions["fr"]["figureTextReplacementMapPath"] in (None, "")
        )

    def test_french_image_root_is_not_a_symlink_to_english_assets(self) -> None:
        french_images_root = ROOT_DIR / "editions" / "fr" / "content" / "images"

        self.assertTrue(french_images_root.exists())
        self.assertFalse(french_images_root.is_symlink())

    def test_landing_generation_writes_english_and_french_variants(self) -> None:
        english_index = (self.output_root / "index.html").read_text(encoding="utf-8")
        french_index = (self.output_root / "fr" / "index.html").read_text(encoding="utf-8")

        self.assertIn('lang="en"', english_index)
        self.assertIn('lang="fr"', french_index)
        self.assertIn('class="site-language-switch"', english_index)
        self.assertIn('href="/fr/?lang=fr"', english_index)
        self.assertIn("navigator.languages", english_index)
        self.assertIn("/fr/", english_index)
        self.assertIn('href="/?lang=en"', french_index)

    def test_landing_language_switch_keeps_en_then_fr_order_without_label(self) -> None:
        english_index = (self.output_root / "index.html").read_text(encoding="utf-8")
        french_index = (self.output_root / "fr" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('class="site-language-label"', english_index)
        self.assertNotIn('class="site-language-label"', french_index)

        self.assertRegex(
            english_index,
            re.compile(
                r'<nav class="site-language-switch"[^>]*>\s*'
                r'<span class="site-language-option is-current" aria-current="page">EN</span>\s*'
                r'<a class="site-language-option" href="/fr/\?lang=fr" lang="fr" hreflang="fr">FR</a>\s*'
                r'</nav>'
            ),
        )
        self.assertRegex(
            french_index,
            re.compile(
                r'<nav class="site-language-switch"[^>]*>\s*'
                r'<a class="site-language-option" href="/\?lang=en" lang="en" hreflang="en">EN</a>\s*'
                r'<span class="site-language-option is-current" aria-current="page">FR</span>\s*'
                r'</nav>'
            ),
        )

    def test_legal_and_chapters_generation_publish_french_routes(self) -> None:
        french_terms = (self.output_root / "fr" / "terms-of-use.html").read_text(encoding="utf-8")
        french_chapters = (self.output_root / "fr" / "chapters" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("Conditions d’utilisation", french_terms)
        self.assertIn('class="site-language-switch"', french_terms)
        self.assertIn("Bibliothèque des chapitres", french_chapters)
        self.assertIn('class="site-language-switch"', french_chapters)

    def test_french_landing_hero_uses_french_copy(self) -> None:
        french_index = (self.output_root / "fr" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Intelligence pétrolière ouest-africaine", french_index)
        self.assertIn("Explorer la couche pays", french_index)

    def test_english_reference_cards_do_not_render_escaped_html_descriptions(self) -> None:
        english_chapters = (self.output_root / "chapters" / "index.html").read_text(encoding="utf-8")

        figures_match = re.search(
            r"<h3>List of Figures</h3>\s*<p>(.*?)</p>",
            english_chapters,
            re.DOTALL,
        )
        tables_match = re.search(
            r"<h3>List of Tables</h3>\s*<p>(.*?)</p>",
            english_chapters,
            re.DOTALL,
        )

        self.assertIsNotNone(figures_match)
        self.assertIsNotNone(tables_match)

        figures_description = figures_match.group(1)
        tables_description = tables_match.group(1)

        self.assertIn("Auxiliary figure index for the web edition.", figures_description)
        self.assertNotIn("&lt;div", figures_description)
        self.assertNotIn("reference-index-figures", figures_description)

        self.assertIn("Auxiliary table index for the web edition.", tables_description)
        self.assertNotIn("&lt;div", tables_description)
        self.assertNotIn("reference-index-tables", tables_description)

    def test_english_chapter_library_tracks_replacement_book_topology(self) -> None:
        english_chapters = (self.output_root / "chapters" / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "Exploration and Production of Petroleum Resources in West Africa",
            english_chapters,
        )
        self.assertIn("/book/chapters/chapter-01-general-introduction.html", english_chapters)
        self.assertIn("/book/chapters/chapter-12-vision-for-west-africa-2050.html", english_chapters)
        self.assertIn("/book/chapters/glossary.html", english_chapters)
        self.assertNotIn(
            "/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            english_chapters,
        )
        self.assertNotIn("/book/chapters/general-conclusion.html", english_chapters)


if __name__ == "__main__":
    unittest.main()
