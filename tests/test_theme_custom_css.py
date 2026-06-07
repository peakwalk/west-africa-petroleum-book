from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CUSTOM_CSS_PATH = ROOT_DIR / "theme/custom.css"
CUSTOM_JS_PATH = ROOT_DIR / "theme/custom.js"


def _rule_block(css: str, selector: str) -> str:
    pattern = re.compile(rf"(?m)^[ \t]*{re.escape(selector)}\s*\{{(?P<body>.*?)\n\}}", re.DOTALL)
    match = pattern.search(css)
    if match is None:
        raise AssertionError(f"Missing CSS rule for {selector}")
    return match.group("body")


class ThemeCustomCssTest(unittest.TestCase):
    def test_figure_card_uses_border_box_layout(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-card")

        self.assertIn("box-sizing: border-box;", block)
        self.assertIn("--figure-card-padding:", block)
        self.assertIn("--figure-media-padding:", block)
        self.assertIn("--figure-divider-gap:", block)
        self.assertIn("--figure-caption-gap:", block)

    def test_figure_images_stay_within_card_width(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-card img")

        self.assertIn("box-sizing: border-box;", block)
        self.assertIn("max-width: 100%;", block)

    def test_figure_media_uses_shared_stage_tokens(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-media")

        self.assertIn("padding: var(--figure-media-padding);", block)
        self.assertIn("border: var(--figure-media-border);", block)
        self.assertIn("background: var(--figure-media-bg);", block)
        self.assertIn("margin: 0 auto var(--figure-divider-gap);", block)

    def test_figure_caption_spacing_is_tokenized(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-caption")

        self.assertIn("padding: var(--figure-caption-gap) var(--figure-caption-inline-padding) 0;", block)
        self.assertIn("border-top: 1px solid rgba(43, 91, 166, 0.12);", block)

    def test_legacy_figure_id_overrides_are_replaced_by_modifiers(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertNotIn("#figure-2.figure-card--multi", css)
        self.assertNotIn("#figure-7.figure-card--multi", css)
        self.assertIn("figure-card--flush-media", css)
        self.assertIn("figure-card--inset-media", css)
        self.assertIn("figure-card--flush-media", js)
        self.assertIn("figure-card--inset-media", js)


if __name__ == "__main__":
    unittest.main()
