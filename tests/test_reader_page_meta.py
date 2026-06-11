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

    def test_chapter_reference_sections_match_outline_visibility_rules(self) -> None:
        expected_sections = {
            "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html": {
                "figures": True,
                "tables": True,
                "formulas": False,
            },
            "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html": {
                "figures": True,
                "tables": True,
                "formulas": True,
            },
            "chapters/chapter-03-tax-regimes-in-the-petroleum-sector.html": {
                "figures": True,
                "tables": False,
                "formulas": False,
            },
            "chapters/chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html": {
                "figures": True,
                "tables": True,
                "formulas": True,
            },
            "chapters/chapter-05-key-socio-political-determinants-of-oil-sector-performance.html": {
                "figures": False,
                "tables": False,
                "formulas": False,
            },
            "chapters/chapter-06-west-africa-in-depth-country-analysis.html": {
                "figures": False,
                "tables": False,
                "formulas": False,
            },
        }

        for page_key, expected in expected_sections.items():
            with self.subTest(page_key=page_key):
                self.assertEqual(expected, self.reader_page_meta[page_key]["referenceSections"])


if __name__ == "__main__":
    unittest.main()
