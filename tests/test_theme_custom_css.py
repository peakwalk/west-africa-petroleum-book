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
        self.assertIn("--figure-card-padding-block: 20px;", block)
        self.assertIn("--figure-card-padding-inline: 24px;", block)
        self.assertIn("--figure-card-bg: var(--sidebar-bg);", block)
        self.assertIn("--figure-media-padding: 0;", block)
        self.assertIn("--figure-divider-gap:", block)
        self.assertIn("--figure-caption-gap:", block)
        self.assertIn("padding: var(--figure-card-padding-block) var(--figure-card-padding-inline);", block)
        self.assertNotIn("padding-bottom:", block)
        self.assertNotIn("linear-gradient(", block)

    def test_figure_images_stay_within_card_width(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-card img")

        self.assertIn("box-sizing: border-box;", block)
        self.assertIn("max-width: 100%;", block)

    def test_figure_media_uses_shared_stage_tokens(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-media")

        self.assertIn(".content p.figure-media,", css)
        self.assertIn("padding: var(--figure-media-padding) 0;", block)
        self.assertIn("border-block: var(--figure-media-border);", block)
        self.assertIn("border-inline: 0;", block)
        self.assertIn("background: var(--figure-media-bg);", block)
        self.assertIn("margin: 0;", block)
        self.assertIn("max-width: 100%;", block)

    def test_figure_footer_has_no_divider_rule(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        footer_block = _rule_block(css, ".figure-card-footer")

        self.assertIn("border-top: 0;", footer_block)
        self.assertNotIn("--figure-divider-extra-inset:", css)
        self.assertNotIn(".figure-card-footer::before", css)

    def test_figure_caption_spacing_is_tokenized(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".figure-card-footer")
        label_icon_block = _rule_block(css, ".figure-card-label::before")

        self.assertIn(
            "padding: var(--figure-caption-gap) calc(var(--reader-figure-caption-inset) + var(--figure-card-padding-inline)) 0;",
            block,
        )
        self.assertIn("text-align: center;", block)
        self.assertIn("width: 24px;", label_icon_block)
        self.assertIn("height: 24px;", label_icon_block)

    def test_figure_media_spacing_has_no_per_figure_geometry_overrides(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertNotIn("#figure-2.figure-card--multi", css)
        self.assertNotIn("#figure-7.figure-card--multi", css)
        self.assertNotIn("figure-card--flush-media", css)
        self.assertNotIn("figure-card--inset-media", css)
        self.assertNotIn("figure-card--flush-media", js)
        self.assertNotIn("figure-card--inset-media", js)
        self.assertNotIn("max-width: calc(var(--figure-media-max-width) - 0.25rem);", css)
        self.assertIn("figure-card--panel-pair", css)
        self.assertIn("figure-card--panel-pair", js)

    def test_table_layout_uses_card_container(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        card_block = _rule_block(css, ".table-card")
        shell_block = _rule_block(css, ".table-anchor-shell")
        scroll_block = _rule_block(css, ".table-scroll")
        target_card_block = _rule_block(css, ".table-anchor-target:target .table-card")
        multirow_header_block = _rule_block(css, ".content thead tr + tr th")
        rowspan_header_block = _rule_block(css, ".content thead th[rowspan]")
        split_header_block = _rule_block(css, ".content thead th + th")
        even_row_block = _rule_block(css, ".content tbody tr:nth-child(even) td")
        table_6_even_row_block = _rule_block(css, "#table-6 .table-data-table tbody tr:nth-child(even) td")
        caption_block = _rule_block(css, ".content .table-caption")
        caption_label_block = _rule_block(css, ".table-caption-label")
        caption_label_icon_block = _rule_block(css, ".table-caption-label::before")
        notes_group_block = _rule_block(css, ".table-notes-group")
        notes_block = _rule_block(css, ".content .table-notes")
        caption_text_block = _rule_block(css, ".table-caption-text")
        table_6_second_header_block = _rule_block(css, "#table-6 .table-data-table thead tr:last-child th")

        self.assertIn("display: grid;", card_block)
        self.assertIn("padding: 24px;", card_block)
        self.assertIn("gap: 0;", card_block)
        self.assertIn("border: 1px solid rgba(148, 163, 184, 0.22);", card_block)
        self.assertIn("background: var(--sidebar-bg);", card_block)
        self.assertIn("box-shadow: 0 14px 28px rgba(15, 23, 42, 0.05);", card_block)
        self.assertNotIn("linear-gradient(", card_block)
        self.assertIn("border-color: rgba(43, 91, 166, 0.22);", target_card_block)
        self.assertNotIn("background:", target_card_block)
        self.assertNotIn("box-shadow:", target_card_block)
        self.assertIn("border: 0;", shell_block)
        self.assertIn("padding: 0;", scroll_block)
        self.assertRegex(css, r"\.content td p,\s*\.content th p \{[^}]*margin:\s*0;")
        self.assertIn("background: rgba(56, 94, 170, 0.96);", multirow_header_block)
        self.assertIn("color: #ffffff;", multirow_header_block)
        self.assertIn("border-top: 2px solid rgba(255, 255, 255, 0.18);", multirow_header_block)
        self.assertIn("vertical-align: middle;", rowspan_header_block)
        self.assertIn("border-left-color: rgba(255, 255, 255, 0.12);", split_header_block)
        self.assertIn(".content td {\n  background: var(--paper);\n}", css)
        self.assertIn("background: var(--paper);", even_row_block)
        self.assertIn("background: var(--paper);", table_6_even_row_block)
        self.assertIn("max-width: none;", caption_block)
        self.assertIn("display: grid;", caption_block)
        self.assertIn("justify-items: start;", caption_block)
        self.assertIn("row-gap: 8px;", caption_block)
        self.assertIn("margin-bottom: 24px;", caption_block)
        self.assertIn("display: grid;", caption_label_block)
        self.assertIn("grid-auto-flow: column;", caption_label_block)
        self.assertIn("justify-content: start;", caption_label_block)
        self.assertIn("display: block;", caption_label_icon_block)
        self.assertIn("width: 24px;", caption_label_icon_block)
        self.assertIn("height: 24px;", caption_label_icon_block)
        self.assertIn("-webkit-mask:", caption_label_icon_block)
        self.assertIn("mask:", caption_label_icon_block)
        self.assertIn("data:image/svg+xml", caption_label_icon_block)
        self.assertIn("font-size: 14px;", caption_text_block)
        self.assertIn("display: block;", caption_text_block)
        self.assertIn("padding-inline-start: calc(24px + 0.55rem);", caption_text_block)
        self.assertIn("color: var(--ink);", caption_text_block)
        self.assertIn("font-style: normal;", caption_text_block)
        self.assertNotIn("font-style: italic;", caption_text_block)
        self.assertNotIn("font-size: 16px;", caption_text_block)
        self.assertNotIn("line-height: 0;", caption_text_block)
        self.assertIn("color: #ffffff;", table_6_second_header_block)
        self.assertIn("font-style: normal;", table_6_second_header_block)
        self.assertNotIn("font-style: italic;", table_6_second_header_block)
        self.assertNotIn("color: rgba(30, 58, 138, 0.82);", table_6_second_header_block)
        self.assertIn("margin-top: 0.6rem;", notes_group_block)
        self.assertIn("margin-bottom: 0;", notes_block)
        self.assertIn('const tableCard = document.createElement("div");', js)
        self.assertIn('tableCard.className = "table-card";', js)
        self.assertIn("wrapper.appendChild(tableCard);", js)
        self.assertIn("tableCard.appendChild(caption);", js)
        self.assertIn("tableCard.appendChild(tableShell);", js)
        self.assertIn("tableCard.appendChild(notesGroup);", js)

    def test_table_formula_cards_use_compact_padding_without_radius(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        start = css.index(".reader-article td .book-formula,")
        end = css.index("}\n\n.api-density-formula-term", start)
        block = css[start : end + 1]

        self.assertIn("padding: 4px;", block)
        self.assertIn("border-radius: 0;", block)
        self.assertNotIn("padding: 0.6rem 0.8rem;", block)
        self.assertNotIn("border-radius: 0.8rem;", block)


if __name__ == "__main__":
    unittest.main()
