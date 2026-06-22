from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.check_docx_parity import _docx_expected_titles, chapter_anchor


class CheckDocxParityTests(unittest.TestCase):
    def test_chapter_anchor_prefers_first_visible_body_block_over_first_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chapter_path = Path(tmpdir) / "chapter.md"
            chapter_path.write_text(
                "\n".join(
                    [
                        "# Chapitre 6 : Afrique de l’Ouest : analyses approfondies par pays",
                        "",
                        "## 6.1- Nigeria",
                        "",
                        "Le Nigéria est le premier producteur de pétrole d'Afrique.",
                        "",
                        "## 6.2- Ghana",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            anchor = chapter_anchor(SimpleNamespace(source_path=str(chapter_path), body=[], outline=[], title=""))

            self.assertEqual(
                anchor,
                "Le Nigéria est le premier producteur de pétrole d'Afrique.",
            )

    def test_docx_expected_titles_strip_body_chapter_prefixes_but_keep_back_matter(self) -> None:
        chapters = [
            SimpleNamespace(
                source_path="/tmp/chapters/chapter-12-vision-for-west-africa-2050.md",
                title="Chapter 12: Vision for West Africa 2050",
            ),
            SimpleNamespace(
                source_path="/tmp/chapters/glossary.md",
                title="Glossary",
            ),
            SimpleNamespace(
                source_path="/tmp/chapters/bibliographical-references.md",
                title="Bibliographical References",
            ),
        ]

        self.assertEqual(
            _docx_expected_titles(chapters),
            [
                "Vision for West Africa 2050",
                "Glossary",
                "Bibliographical References",
            ],
        )

    def test_docx_expected_titles_strip_french_body_chapter_prefixes(self) -> None:
        chapters = [
            SimpleNamespace(
                source_path="/tmp/chapters/chapter-06-west-africa-in-depth-country-analysis.md",
                title="Chapitre 6 : Afrique de l’Ouest : analyses approfondies par pays",
            ),
            SimpleNamespace(
                source_path="/tmp/chapters/glossary.md",
                title="Glossaire",
            ),
        ]

        self.assertEqual(
            _docx_expected_titles(chapters),
            [
                "Afrique de l’Ouest : analyses approfondies par pays",
                "Glossaire",
            ],
        )


if __name__ == "__main__":
    unittest.main()
