from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = ROOT_DIR / "package.json"


class FigureEditionScriptTests(unittest.TestCase):
    def test_package_scripts_expose_french_and_dual_edition_figure_checks(self) -> None:
        scripts = json.loads(PACKAGE_JSON_PATH.read_text(encoding="utf-8"))["scripts"]

        self.assertIn("build:docx-figure-manifest:en", scripts)
        self.assertIn("build:docx-figure-manifest:fr", scripts)
        self.assertIn("check:docx-figures:en", scripts)
        self.assertIn("check:docx-figures:fr", scripts)
        self.assertIn("check:docx-figures:all", scripts)
        self.assertIn("check:docx-parity:en", scripts)
        self.assertIn("check:docx-parity:fr", scripts)
        self.assertIn("check:docx-parity:all", scripts)
        self.assertIn("--edition fr", scripts["check:docx-figures:fr"])
        self.assertIn("--edition fr", scripts["check:docx-parity:fr"])


if __name__ == "__main__":
    unittest.main()
