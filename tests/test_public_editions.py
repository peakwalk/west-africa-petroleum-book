from __future__ import annotations

import json
import re
import shutil
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
        cls._backups: list[tuple[Path, Path]] = []

        for relative_path in [
            Path("index.html"),
            Path("terms-of-use.html"),
            Path("privacy-policy.html"),
            Path("cookie-policy.html"),
            Path("chapters/index.html"),
            Path("fr"),
        ]:
            source_path = ROOT_DIR / relative_path
            if not source_path.exists():
                continue

            backup_path = cls._temp_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.is_dir():
                shutil.copytree(source_path, backup_path)
            else:
                shutil.copy2(source_path, backup_path)
            cls._backups.append((source_path, backup_path))

        subprocess.run(
            ["node", "scripts/generate-index-page.mjs"],
            cwd=ROOT_DIR,
            check=True,
        )
        subprocess.run(
            ["node", "scripts/generate-legal-pages.mjs"],
            cwd=ROOT_DIR,
            check=True,
        )
        subprocess.run(
            ["node", "scripts/generate-chapters-page.mjs"],
            cwd=ROOT_DIR,
            check=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        for relative_path in [
            Path("fr"),
            Path("index.html"),
            Path("terms-of-use.html"),
            Path("privacy-policy.html"),
            Path("cookie-policy.html"),
            Path("chapters/index.html"),
        ]:
            target_path = ROOT_DIR / relative_path
            if target_path.is_dir():
                shutil.rmtree(target_path, ignore_errors=True)
            else:
                target_path.unlink(missing_ok=True)

        for target_path, backup_path in cls._backups:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if backup_path.is_dir():
                shutil.copytree(backup_path, target_path)
            else:
                shutil.copy2(backup_path, target_path)

        shutil.rmtree(cls._temp_dir, ignore_errors=True)

    def test_shared_registry_declares_english_and_french_editions(self) -> None:
        registry = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        self.assertEqual(["en", "fr"], [edition["locale"] for edition in registry["editions"]])

    def test_shared_registry_declares_locale_scoped_figure_roots(self) -> None:
        registry = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        editions = {edition["locale"]: edition for edition in registry["editions"]}

        self.assertEqual("src/images", editions["en"]["figureRoot"])
        self.assertEqual(
            "src/images/figure-manifest.json",
            editions["en"]["figureManifestPath"],
        )
        self.assertEqual(
            "scripts/docx_figures/figure_text_englishization_map.json",
            editions["en"]["figureTextReplacementMapPath"],
        )

        self.assertEqual("src-fr/images", editions["fr"]["figureRoot"])
        self.assertEqual(
            "src-fr/images/figure-manifest.json",
            editions["fr"]["figureManifestPath"],
        )
        self.assertTrue(
            "figureTextReplacementMapPath" not in editions["fr"]
            or editions["fr"]["figureTextReplacementMapPath"] in (None, "")
        )

    def test_french_image_root_is_not_a_symlink_to_english_assets(self) -> None:
        french_images_root = ROOT_DIR / "src-fr" / "images"

        self.assertTrue(french_images_root.exists())
        self.assertFalse(french_images_root.is_symlink())

    def test_landing_generation_writes_english_and_french_variants(self) -> None:
        english_index = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
        french_index = (ROOT_DIR / "fr" / "index.html").read_text(encoding="utf-8")

        self.assertIn('lang="en"', english_index)
        self.assertIn('lang="fr"', french_index)
        self.assertIn('class="site-language-switch"', english_index)
        self.assertIn('href="/fr/?lang=fr"', english_index)
        self.assertIn("navigator.languages", english_index)
        self.assertIn("/fr/", english_index)
        self.assertIn('href="/?lang=en"', french_index)

    def test_landing_language_switch_keeps_en_then_fr_order_without_label(self) -> None:
        english_index = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
        french_index = (ROOT_DIR / "fr" / "index.html").read_text(encoding="utf-8")

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
        french_terms = (ROOT_DIR / "fr" / "terms-of-use.html").read_text(encoding="utf-8")
        french_chapters = (ROOT_DIR / "fr" / "chapters" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("Conditions d’utilisation", french_terms)
        self.assertIn('class="site-language-switch"', french_terms)
        self.assertIn("Bibliothèque des chapitres", french_chapters)
        self.assertIn('class="site-language-switch"', french_chapters)

    def test_french_landing_hero_uses_french_copy(self) -> None:
        french_index = (ROOT_DIR / "fr" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Intelligence pétrolière ouest-africaine", french_index)
        self.assertIn("Explorer la couche pays", french_index)

    def test_english_reference_cards_do_not_render_escaped_html_descriptions(self) -> None:
        english_chapters = (ROOT_DIR / "chapters" / "index.html").read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
