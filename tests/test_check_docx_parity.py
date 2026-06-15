from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.check_docx_parity import chapter_anchor


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


if __name__ == "__main__":
    unittest.main()
