from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from scripts.edition_config import get_edition


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "editions.json"


class EditionWorkspaceLayoutTests(unittest.TestCase):
    def test_edition_workspaces_have_symmetric_core_structure(self) -> None:
        for locale in ("en", "fr"):
            edition_root = ROOT_DIR / "editions" / locale

            self.assertTrue((edition_root / "book.toml").exists())
            self.assertTrue((edition_root / "locale.json").exists())
            self.assertTrue((edition_root / "site").is_dir())
            self.assertTrue((edition_root / "site" / "legal").is_dir())
            self.assertTrue((edition_root / "source").is_dir())
            self.assertTrue((edition_root / "source" / "images").is_dir())
            self.assertTrue((edition_root / "content").is_dir())
            self.assertTrue((edition_root / "content" / "chapters").is_dir())
            self.assertTrue((edition_root / "content" / "images").is_dir())
            self.assertTrue((edition_root / "content" / "SUMMARY.md").exists())
            self.assertTrue((edition_root / "content" / "images" / "figure-manifest.json").exists())
            self.assertTrue((edition_root / "source" / "images" / "figure-000.png").exists())
            self.assertFalse((edition_root / "content" / "images" / "figure-000.png").exists())

    def test_registry_declares_edition_root_contract(self) -> None:
        registry = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        editions = {edition["locale"]: edition for edition in registry["editions"]}
        self.assertEqual("editions/en", editions["en"]["editionRoot"])
        self.assertEqual("editions/fr", editions["fr"]["editionRoot"])

        for locale in ("en", "fr"):
            self.assertNotIn("bookRoot", editions[locale])
            self.assertNotIn("sourceRoot", editions[locale])
            self.assertNotIn("summaryPath", editions[locale])
            self.assertNotIn("chapterRoot", editions[locale])
            self.assertNotIn("legalRoot", editions[locale])
            self.assertNotIn("figureRoot", editions[locale])
            self.assertNotIn("figureManifestPath", editions[locale])
            self.assertNotIn("localeCatalog", editions[locale])

    def test_python_loader_derives_paths_from_edition_root(self) -> None:
        english = get_edition("en")
        french = get_edition("fr")

        self.assertEqual(ROOT_DIR / "editions" / "en", english.edition_root)
        self.assertEqual(ROOT_DIR / "editions" / "fr", french.edition_root)

        for edition in (english, french):
            self.assertEqual(edition.edition_root, edition.book_root)
            self.assertEqual(edition.edition_root / "book.toml", edition.book_config_path)
            self.assertEqual(edition.edition_root / "locale.json", edition.locale_catalog_path)
            self.assertEqual(edition.edition_root / "content", edition.source_root)
            self.assertEqual(edition.edition_root / "content" / "SUMMARY.md", edition.summary_path)
            self.assertEqual(edition.edition_root / "content" / "chapters", edition.chapter_root)
            self.assertEqual(edition.edition_root / "site" / "legal", edition.legal_root)
            self.assertEqual(edition.edition_root / "content" / "images", edition.figure_root)
            self.assertEqual(
                edition.edition_root / "content" / "images" / "figure-manifest.json",
                edition.figure_manifest_path,
            )

    def test_node_and_python_loaders_resolve_matching_paths(self) -> None:
        result = subprocess.run(
            [
                "node",
                "--input-type=module",
                "-e",
                """
import { listSiteEditions } from "./scripts/shared/site-editions.mjs";
const payload = listSiteEditions().map((edition) => ({
  locale: edition.locale,
  editionRoot: edition.editionRoot,
  bookRoot: edition.bookRoot,
  bookConfigPath: edition.bookConfigPath,
  sourceRoot: edition.sourceRoot,
  summaryPath: edition.summaryPath,
  chapterRoot: edition.chapterRoot,
  legalRoot: edition.legalRoot,
  figureRoot: edition.figureRoot,
  figureManifestPath: edition.figureManifestPath,
  localeCatalog: edition.localeCatalog,
}));
console.log(JSON.stringify(payload));
                """,
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            check=True,
            text=True,
        )
        node_editions = {
            entry["locale"]: entry for entry in json.loads(result.stdout)
        }

        for locale in ("en", "fr"):
            python_edition = get_edition(locale)
            node_edition = node_editions[locale]

            self.assertEqual(str(python_edition.edition_root.relative_to(ROOT_DIR)), node_edition["editionRoot"])
            self.assertEqual(str(python_edition.book_root.relative_to(ROOT_DIR)), node_edition["bookRoot"])
            self.assertEqual(
                str(python_edition.book_config_path.relative_to(ROOT_DIR)),
                node_edition["bookConfigPath"],
            )
            self.assertEqual(str(python_edition.source_root.relative_to(ROOT_DIR)), node_edition["sourceRoot"])
            self.assertEqual(str(python_edition.summary_path.relative_to(ROOT_DIR)), node_edition["summaryPath"])
            self.assertEqual(str(python_edition.chapter_root.relative_to(ROOT_DIR)), node_edition["chapterRoot"])
            self.assertEqual(str(python_edition.legal_root.relative_to(ROOT_DIR)), node_edition["legalRoot"])
            self.assertEqual(str(python_edition.figure_root.relative_to(ROOT_DIR)), node_edition["figureRoot"])
            self.assertEqual(
                str(python_edition.figure_manifest_path.relative_to(ROOT_DIR)),
                node_edition["figureManifestPath"],
            )
            self.assertEqual(
                str(python_edition.locale_catalog_path.relative_to(ROOT_DIR)),
                node_edition["localeCatalog"],
            )


if __name__ == "__main__":
    unittest.main()
