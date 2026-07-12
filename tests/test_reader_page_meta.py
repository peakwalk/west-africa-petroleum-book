from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
READER_META_PATH = ROOT_DIR / "public/book/reader-page-meta.json"
BOOK_INDEX_PATH = ROOT_DIR / "public/book/index.html"


class ReaderPageMetaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._reader_meta_backup = READER_META_PATH.read_bytes() if READER_META_PATH.exists() else None
        cls._book_index_backup = BOOK_INDEX_PATH.read_bytes() if BOOK_INDEX_PATH.exists() else None

        subprocess.run(
            ["node", "scripts/build_reader_page_meta.mjs"],
            cwd=ROOT_DIR,
            check=True,
        )

        cls.reader_page_meta = json.loads(READER_META_PATH.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._reader_meta_backup is None:
            READER_META_PATH.unlink(missing_ok=True)
        else:
            READER_META_PATH.write_bytes(cls._reader_meta_backup)

        if cls._book_index_backup is None:
            BOOK_INDEX_PATH.unlink(missing_ok=True)
        else:
            BOOK_INDEX_PATH.write_bytes(cls._book_index_backup)

    def test_reader_page_meta_tracks_replacement_english_page_inventory(self) -> None:
        expected_page_keys = {
            "chapters/cover.html",
            "chapters/disclaimer.html",
            "chapters/preface.html",
            "chapters/table-of-contents.html",
            "chapters/list-of-figures.html",
            "chapters/list-of-tables.html",
            "chapters/list-of-equations.html",
            "chapters/abbreviations-acronyms-and-abbreviations.html",
            "chapters/foreword.html",
            "chapters/foreword-to-the-french-edition.html",
            "chapters/chapter-01-general-introduction.html",
            "chapters/chapter-02-emerging-petroleum-provinces-in-west-africa.html",
            "chapters/chapter-03-west-africa-country-analysis.html",
            "chapters/chapter-04-national-oil-companies-in-west-africa.html",
            "chapters/chapter-05-hydrocarbon-value-chain.html",
            "chapters/chapter-06-upstream-operations-and-government-roles.html",
            "chapters/chapter-08-petroleum-fiscal-regimes.html",
            "chapters/chapter-09-west-african-fiscal-regimes.html",
            "chapters/chapter-10-socio-political-determinants.html",
            "chapters/chapter-07-petroleum-data-management-in-west-africa.html",
            "chapters/chapter-11-general-conclusion.html",
            "chapters/chapter-12-vision-for-west-africa-2050.html",
            "chapters/glossary.html",
            "chapters/bibliographical-references.html",
        }

        self.assertTrue(expected_page_keys.issubset(self.reader_page_meta.keys()))
        self.assertNotIn(
            "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            self.reader_page_meta,
        )
        self.assertNotIn("chapters/general-conclusion.html", self.reader_page_meta)

    def test_reader_page_meta_parses_replacement_titles_and_eyebrows(self) -> None:
        chapter_one = self.reader_page_meta["chapters/chapter-01-general-introduction.html"]
        chapter_eleven = self.reader_page_meta["chapters/chapter-11-general-conclusion.html"]
        foreword = self.reader_page_meta["chapters/foreword.html"]
        french_edition_foreword = self.reader_page_meta["chapters/foreword-to-the-french-edition.html"]
        glossary = self.reader_page_meta["chapters/glossary.html"]
        disclaimer = self.reader_page_meta["chapters/disclaimer.html"]

        self.assertEqual("Chapter 1", chapter_one["eyebrow"])
        self.assertEqual("General Introduction", chapter_one["title"])
        self.assertEqual("Chapter 11", chapter_eleven["eyebrow"])
        self.assertEqual("General Conclusion", chapter_eleven["title"])
        self.assertEqual("", foreword["eyebrow"])
        self.assertEqual("Foreword to the English Edition", foreword["title"])
        self.assertEqual("", french_edition_foreword["eyebrow"])
        self.assertEqual("Foreword to the French Edition", french_edition_foreword["title"])
        self.assertEqual("", glossary["eyebrow"])
        self.assertEqual("Glossary", glossary["title"])
        self.assertEqual("", disclaimer["eyebrow"])
        self.assertEqual("DISCLAIMER", disclaimer["title"])


if __name__ == "__main__":
    unittest.main()
