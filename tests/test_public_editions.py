from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "editions.json"
RETIRED_LANDING_IMAGE_ASSETS = (
    "cover.png",
    "homepage-west-africa-map-panel.png",
    "homepage-west-africa-map-panel.webp",
    "homepage-west-africa-map-panel@2x.png",
    "prototype-hero-cutout.png",
    "prototype-hero-edge-left.png",
    "prototype-hero-edge-right.png",
    "prototype-hero-grayscale-left.png",
    "prototype-hero-grayscale-right.png",
    "prototype-hero-overlay.png",
    "upstream-atlas-hero-v2-photo.png",
    "upstream-atlas-logo.png",
    "upstream-atlas-nav-logo.png",
)
RETIRED_HOMEPAGE_CROPPED_ICON_PNG_ASSETS = (
    "icon-audience-operators.png",
    "icon-audience-policy.png",
    "icon-audience-research.png",
    "icon-exploration.png",
    "icon-fiscal.png",
    "icon-industry-monitoring.png",
    "icon-intelligence.png",
    "icon-production.png",
    "icon-regulation.png",
    "icon-research.png",
)
RETIRED_UNREFERENCED_LANDING_ASSET_VARIANTS = (
    "homepage-cabo-verde-inset.svg",
    "prototype-hero-dusk.webp",
    "prototype-hero-night.webp",
    "prototype-hero-sunset-right.webp",
    "prototype-hero-sunset-source.webp",
    "prototype-hero.jpg",
    "upstream-atlas-hero-v2-photo-right-fade.webp",
    "upstream-atlas-hero-v3-clean.webp",
    "upstream-atlas-hero-v4-clean.webp",
    "upstream-atlas-hero-v5-soft-left.webp",
    "upstream-atlas-hero-v6-soft-left.webp",
    "upstream-atlas-wordmark.png",
    "west-africa-intelligence-overlay.svg",
)


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

    def test_current_edition_cover_uses_optimized_webp_delivery(self) -> None:
        english_index = (self.output_root / "index.html").read_text(encoding="utf-8")
        cover_png = ROOT_DIR / "assets" / "images" / "upstream-atlas-hero-book.png"
        cover_webp = ROOT_DIR / "assets" / "images" / "upstream-atlas-hero-book.webp"

        self.assertTrue(cover_webp.exists())
        self.assertLess(cover_webp.stat().st_size, cover_png.stat().st_size)
        self.assertLess(cover_webp.stat().st_size, 150_000)

        self.assertIn('src="assets/images/upstream-atlas-hero-book.webp"', english_index)
        self.assertIn('loading="lazy"', english_index)
        self.assertIn('decoding="async"', english_index)
        self.assertNotIn('src="assets/images/upstream-atlas-hero-book.png"', english_index)

    def test_landing_shell_uses_split_favicon_delivery(self) -> None:
        english_index = (self.output_root / "index.html").read_text(encoding="utf-8")
        french_index = (self.output_root / "fr" / "index.html").read_text(encoding="utf-8")
        favicon_source = ROOT_DIR / "assets" / "images" / "upstream-atlas-favicon.png"
        favicon_32 = ROOT_DIR / "assets" / "images" / "upstream-atlas-favicon-32.png"
        apple_touch_icon = ROOT_DIR / "assets" / "images" / "upstream-atlas-apple-touch-icon.png"

        self.assertTrue(favicon_32.exists())
        self.assertTrue(apple_touch_icon.exists())
        self.assertLess(favicon_32.stat().st_size, 5_000)
        self.assertLess(apple_touch_icon.stat().st_size, favicon_source.stat().st_size)
        self.assertLess(apple_touch_icon.stat().st_size, 30_000)

        for homepage_html in (english_index, french_index):
            self.assertIn('rel="icon" href="assets/images/upstream-atlas-favicon-32.png', homepage_html)
            self.assertIn('rel="shortcut icon" href="assets/images/upstream-atlas-favicon-32.png', homepage_html)
            self.assertIn('rel="apple-touch-icon" href="assets/images/upstream-atlas-apple-touch-icon.png', homepage_html)
            self.assertNotIn('assets/images/upstream-atlas-favicon.png?v=2', homepage_html)

    def test_retired_landing_image_assets_are_absent_from_source_tree(self) -> None:
        assets_root = ROOT_DIR / "assets" / "images"

        for asset_name in RETIRED_LANDING_IMAGE_ASSETS:
            with self.subTest(asset_name=asset_name):
                self.assertFalse((assets_root / asset_name).exists())

    def test_retired_homepage_cropped_icon_png_assets_are_absent_from_source_tree(self) -> None:
        assets_root = ROOT_DIR / "assets" / "icons" / "homepage-cropped"

        for asset_name in RETIRED_HOMEPAGE_CROPPED_ICON_PNG_ASSETS:
            with self.subTest(asset_name=asset_name):
                self.assertFalse((assets_root / asset_name).exists())

    def test_unreferenced_landing_asset_variants_are_absent_from_source_tree(self) -> None:
        assets_root = ROOT_DIR / "assets" / "images"

        for asset_name in RETIRED_UNREFERENCED_LANDING_ASSET_VARIANTS:
            with self.subTest(asset_name=asset_name):
                self.assertFalse((assets_root / asset_name).exists())

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
        equations_match = re.search(
            r"<h3>List of Equations</h3>\s*<p>(.*?)</p>",
            english_chapters,
            re.DOTALL,
        )

        self.assertIsNotNone(figures_match)
        self.assertIsNotNone(tables_match)
        self.assertIsNotNone(equations_match)

        figures_description = figures_match.group(1)
        tables_description = tables_match.group(1)
        equations_description = equations_match.group(1)

        self.assertIn("Auxiliary figure index for the web edition.", figures_description)
        self.assertNotIn("&lt;div", figures_description)
        self.assertNotIn("reference-index-figures", figures_description)

        self.assertIn("Auxiliary table index for the web edition.", tables_description)
        self.assertNotIn("&lt;div", tables_description)
        self.assertNotIn("reference-index-tables", tables_description)

        self.assertIn("Auxiliary equation index for the web edition.", equations_description)
        self.assertNotIn("&lt;div", equations_description)
        self.assertNotIn("reference-index-equations", equations_description)

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
