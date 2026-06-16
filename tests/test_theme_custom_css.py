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
    def test_reader_article_unordered_lists_include_padding_within_body_width(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".reader-article ul")

        self.assertIn("box-sizing: border-box;", block)
        self.assertIn("max-width: min(100%, var(--reader-article-body-width));", block)
        self.assertIn("margin-inline: auto;", block)

    def test_reader_article_ordered_lists_align_with_body_copy(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".reader-article ol")

        self.assertIn("margin-left: 0;", block)
        self.assertIn("padding-left: 0;", block)
        self.assertIn("padding-inline-start: 0;", block)
        self.assertIn("list-style-position: inside;", block)

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

    def test_figure_annotation_accepts_french_caption_spacing_and_panel_pair_variants(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn(r'/^Figure\s+\d+\s*:/i', js)
        self.assertIn(r'/^Figure\s+(\d+)\s*:\s*(.*)$/i', js)
        self.assertIn('"2": ["figure-card--panel-pair"]', js)
        self.assertIn('"7": ["figure-card--panel-pair"]', js)

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
        caption_icon_block = _rule_block(css, ".table-caption-icon")
        caption_label_block = _rule_block(css, ".table-caption-label")
        notes_group_block = _rule_block(css, ".table-notes-group")
        notes_block = _rule_block(css, ".content .table-notes")
        caption_text_block = _rule_block(css, ".table-caption-text")
        table_8_block = _rule_block(css, "#table-8 .table-anchor-table")
        table_6_second_header_block = _rule_block(css, "#table-6 .table-data-table thead tr:last-child th")

        self.assertIn("display: grid;", card_block)
        self.assertIn("padding: var(--reader-table-card-padding);", card_block)
        self.assertIn("gap: 0;", card_block)
        self.assertIn("border: var(--reader-table-card-border);", card_block)
        self.assertIn("background: var(--reader-table-card-bg);", card_block)
        self.assertIn("box-shadow: var(--reader-table-card-shadow);", card_block)
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
        self.assertIn("grid-template-columns: var(--reader-table-caption-icon-size) minmax(0, 1fr);", caption_block)
        self.assertIn("column-gap: 0.55rem;", caption_block)
        self.assertIn("row-gap: 8px;", caption_block)
        self.assertIn("margin-bottom: 24px;", caption_block)
        self.assertIn("grid-row: 1 / span 2;", caption_icon_block)
        self.assertIn("width: var(--reader-table-caption-icon-size);", caption_icon_block)
        self.assertIn("height: var(--reader-table-caption-icon-size);", caption_icon_block)
        self.assertIn("-webkit-mask:", caption_icon_block)
        self.assertIn("mask:", caption_icon_block)
        self.assertIn("data:image/svg+xml", caption_icon_block)
        self.assertIn("grid-column: 2;", caption_label_block)
        self.assertIn("display: block;", caption_label_block)
        self.assertIn("font-size: 14px;", caption_text_block)
        self.assertIn("display: block;", caption_text_block)
        self.assertIn("grid-column: 2;", caption_text_block)
        self.assertNotIn("padding-inline-start:", caption_text_block)
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
        self.assertIn("min-width: 40rem;", table_8_block)
        self.assertIn('const tableCard = document.createElement("div");', js)
        self.assertIn('const captionIcon = document.createElement("span");', js)
        self.assertIn('captionIcon.className = "table-caption-icon";', js)
        self.assertIn('tableCard.className = "table-card";', js)
        self.assertIn("wrapper.dataset.captionPosition = captionPosition;", js)
        self.assertIn("wrapper.appendChild(tableCard);", js)
        self.assertIn("tableCard.appendChild(caption);", js)
        self.assertIn("tableCard.appendChild(tableShell);", js)
        self.assertIn("tableCard.appendChild(notesGroup);", js)
        self.assertRegex(css, r"\.content th p \{[^}]*color:\s*inherit;")

    def test_table_annotation_supports_french_tableau_captions_and_docx_tables(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("Tableau", js)
        self.assertIn("function getLocalizedTableLabel()", js)
        self.assertIn('document.documentElement.lang || "en"', js)
        self.assertIn("function normalizeDocxTableStructure(table)", js)
        self.assertIn('table.classList.contains("t1")', js)
        self.assertIn("table.createTHead()", js)

    def test_mobile_reader_keeps_language_switch_in_toolbar_before_search(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        sidebar_switch_block = _rule_block(css, '.reader-language-switch[data-reader-language-switch="sidebar"]')

        self.assertIn("display: none;", sidebar_switch_block)
        self.assertRegex(
            css,
            re.compile(
                r"@media \(max-width: 1023px\) \{.*?"
                r"\.toolbar-actions \{\s*min-width: 0;\s*padding-inline-start: 0\.5rem;\s*padding-inline-end: 0;\s*gap: 0\.5rem;\s*\}.*?"
                r'\.toolbar-actions \.reader-language-switch\[data-reader-language-switch="toolbar"\] \{.*?display: inline-flex;.*?\}.*?'
                r'#mdbook-search-toggle \{\s*display: inline-flex !important;\s*\}',
                re.DOTALL,
            ),
        )

    def test_mobile_reader_compacts_logo_and_toolbar_switch(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        marker = "@media (max-width: 1023px) {"
        start = css.index(marker)
        next_marker = css.index("\n\n@media", start + len(marker))
        block = css[start:next_marker]

        for expected in [
            ".toolbar-sidebar {",
            "gap: 0.625rem;",
            "padding-inline-end: 0;",
            '.toolbar-actions .reader-language-switch[data-reader-language-switch="toolbar"] {',
            "display: inline-flex;",
            "flex-shrink: 0;",
            "order: 1;",
            "font-size: 0.66rem;",
            "gap: 0.2rem;",
            "padding: 0.2rem 0.25rem;",
            '.toolbar-actions .reader-language-switch[data-reader-language-switch="toolbar"] .reader-language-option {',
            "min-width: 1.55rem;",
            "min-height: 1.55rem;",
            "padding: 0 0.35rem;",
            ".book-home-link {",
            "width: 44px;",
            "height: 44px;",
            "flex: 0 0 44px;",
            "justify-content: center;",
            ".book-home-icon-full {",
            "display: none;",
            ".book-home-icon-compact {",
            "display: block;",
            "width: 32px;",
            "height: 32px;",
        ]:
            self.assertIn(expected, block)

    def test_reader_tablet_logo_uses_narrow_toolbar_with_full_mark(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        marker = "@media (min-width: 768px) and (max-width: 1023px) {"
        start = css.index(marker)
        next_marker = css.index("\n\n@media", start + len(marker))
        block = css[start:next_marker]

        for expected in [
            ".book-home-link {",
            "width: auto;",
            "height: 44px;",
            "flex: 0 0 auto;",
            ".book-home-icon-full {",
            "display: block;",
            "width: auto;",
            "height: 36px;",
            ".book-home-icon-compact {",
            "display: none;",
        ]:
            self.assertIn(expected, block)

    def test_reader_desktop_logo_uses_fixed_height_full_mark(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        marker = "@media (min-width: 1024px) {"
        start = css.rindex(marker)
        next_marker = css.index("\n\n@media", start + len(marker))
        block = css[start:next_marker]

        for expected in [
            ".book-home-icon-full {",
            "width: auto;",
            "height: 36px;",
        ]:
            self.assertIn(expected, block)

    def test_table_formula_cards_use_compact_padding_without_excess_chrome(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        start = css.index(".reader-article td .formula-card,")
        end = css.index("}\n\n.reader-article td .formula-card > .book-formula,", start)
        block = css[start : end + 1]

        self.assertIn("padding: 0.5rem 0.65rem;", block)
        self.assertIn("box-shadow: none;", block)
        self.assertNotIn("padding: var(--reader-table-card-padding);", block)
        self.assertNotIn("box-shadow: var(--reader-table-card-shadow);", block)

    def test_formula_cards_share_table_card_shell_and_notes_layout(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        card_block = _rule_block(css, ".formula-card")
        embedded_block = _rule_block(css, ".formula-card--embedded")
        caption_block = _rule_block(css, ".content .formula-caption")
        label_block = _rule_block(css, ".formula-caption-label")
        nested_formula_block = _rule_block(css, ".formula-card > .book-formula")
        notes_group_block = _rule_block(css, ".formula-notes-group")
        note_block = _rule_block(css, ".content .formula-note")
        note_term_block = _rule_block(css, ".formula-note-term")

        self.assertIn("padding: var(--reader-table-card-padding);", card_block)
        self.assertIn("border: var(--reader-table-card-border);", card_block)
        self.assertIn("background: var(--reader-table-card-bg);", card_block)
        self.assertIn("box-shadow: var(--reader-table-card-shadow);", card_block)
        self.assertIn("padding: 1rem 1.1rem;", embedded_block)
        self.assertIn("box-shadow: none;", embedded_block)
        self.assertIn("margin: 0 0 0.85rem;", caption_block)
        self.assertIn("text-transform: uppercase;", label_block)
        self.assertIn("margin: 0;", nested_formula_block)
        self.assertIn("padding: 0;", nested_formula_block)
        self.assertIn("border: 0;", nested_formula_block)
        self.assertIn("background: transparent;", nested_formula_block)
        self.assertIn("margin-top: 0.2rem;", notes_group_block)
        self.assertIn("font-size: 12px;", note_block)
        self.assertIn("font-weight: 600;", note_term_block)
        self.assertIn('const formulasSection = document.querySelector(".book-outline-formulas");', js)
        self.assertIn("const formulaItems = collectFormulaCards();", js)
        self.assertIn("populateOutlineSection(formulasSection, formulaItems, formulasEnabled);", js)
        self.assertIn('formulaCard.className = "formula-card";', js)
        self.assertIn('captionLabel.textContent = "Equation " + formulaLabel;', js)

    def test_formula_annotation_uses_explicit_equation_labels(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn('document.querySelectorAll(".reader-article [data-equation-label]:not(.book-formula)")', js)
        self.assertIn('document.querySelectorAll(".reader-article .book-formula[data-equation-label]")', js)
        self.assertIn('const formulaLabel = normalizeText(element.dataset.equationLabel || "");', js)
        self.assertIn('formulaWrapper.dataset.formulaNav = "true";', js)
        self.assertIn('document.querySelectorAll(".formula-anchor-target[data-formula-nav=\\"true\\"]")', js)
        self.assertIn('captionLabel.textContent = "Equation " + formulaLabel;', js)
        self.assertNotIn("function getFormulaSubLabel(index)", js)

    def test_outline_reference_sections_are_gated_by_reader_page_meta(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("const referenceSections = pageMeta && pageMeta.referenceSections ? pageMeta.referenceSections : null;", js)
        self.assertIn("const figuresEnabled = !referenceSections || referenceSections.figures !== false;", js)
        self.assertIn("const tablesEnabled = !referenceSections || referenceSections.tables !== false;", js)
        self.assertIn("const formulasEnabled = !referenceSections || referenceSections.formulas !== false;", js)
        self.assertIn("populateOutlineSection(figuresSection, figureItems, figuresEnabled);", js)
        self.assertIn("populateOutlineSection(tablesSection, tableItems, tablesEnabled);", js)
        self.assertIn("populateOutlineSection(formulasSection, formulaItems, formulasEnabled);", js)
        self.assertIn("installOutlineReferenceSections().then(syncOutlineRailVisibility);", js)

    def test_hidden_outline_sections_stay_hidden(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".book-outline-section[hidden]")

        self.assertIn("display: none;", block)

    def test_outline_reference_titles_wrap_without_truncation(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".reader-outline .book-outline-link--reference-title")

        self.assertIn("white-space: normal;", block)
        self.assertNotIn("overflow: hidden;", block)
        self.assertNotIn("display: -webkit-box;", block)
        self.assertNotIn("-webkit-line-clamp:", block)
        self.assertNotIn("const conciseText = truncateReferenceText(primaryClause || normalizedText, 44);", js)

    def test_formula_card_inner_formula_wraps_without_scrollbar(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        nested_formula_block = _rule_block(css, ".formula-card > .book-formula")
        nested_line_block = _rule_block(css, ".formula-card > .book-formula .book-formula-line")

        self.assertIn("overflow: visible;", nested_formula_block)
        self.assertIn("white-space: normal;", nested_formula_block)
        self.assertNotIn("overflow-x: auto;", nested_formula_block)
        self.assertIn("width: 100%;", nested_line_block)
        self.assertIn("min-width: 0;", nested_line_block)
        self.assertNotIn("width: max-content;", nested_line_block)

    def test_formula_where_blocks_and_group_children_are_borderless_inside_cards(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        group_block = _rule_block(
            css,
            ".formula-group > .book-formula,\n.formula-group--split .formula-split-entry > .book-formula,\n.formula-card > .formula-derivation > .book-formula,\n.formula-group .formula-derivation > .book-formula,\n.formula-where .book-formula--local",
        )
        where_block = _rule_block(css, ".formula-where")
        where_label_block = _rule_block(css, ".content .formula-where-label")
        where_item_block = _rule_block(css, ".content .formula-where-item")

        self.assertIn("border: 0;", group_block)
        self.assertIn("background: transparent;", group_block)
        self.assertIn("box-shadow: none;", group_block)
        self.assertIn("border-top: 1px solid rgba(148, 163, 184, 0.22);", where_block)
        self.assertIn("text-transform: uppercase;", where_label_block)
        self.assertIn("font-size: 12px;", where_item_block)

    def test_volumetric_formula_group_uses_clear_visual_hierarchy(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        main_block = _rule_block(css, ".formula-group--volumetric > .book-formula")
        with_label_block = _rule_block(css, ".content .formula-group--volumetric .formula-where-label")
        spec_grid_block = _rule_block(css, ".formula-spec-grid--two")
        spec_copy_block = _rule_block(css, ".formula-where--volumetric .formula-spec-copy")
        local_formula_block = _rule_block(css, ".formula-spec-item .book-formula--local")
        empty_item_block = _rule_block(css, ".formula-spec-item--empty")
        derivation_block = _rule_block(css, ".formula-derivation--volumetric")
        case_block = _rule_block(css, ".formula-group--volumetric .formula-case")
        case_title_block = _rule_block(css, ".formula-group--volumetric .formula-case-title")
        case_stack_block = _rule_block(css, ".formula-group--volumetric .formula-case-stack")
        case_formula_block = _rule_block(css, ".formula-group--volumetric .formula-case .book-formula")
        case_note_shell_block = _rule_block(css, ".formula-case-note")
        case_note_block = _rule_block(css, ".formula-case-note .formula-note")

        self.assertIn("font-size: clamp(20px, 1.55vw, 25px);", main_block)
        self.assertIn("font-size: 11px;", with_label_block)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", spec_grid_block)
        self.assertIn("font-size: 12.5px;", spec_copy_block)
        self.assertIn("font-size: clamp(12.7px, 0.92vw, 14.4px);", local_formula_block)
        self.assertIn("background: rgba(255, 255, 255, 0.96);", empty_item_block)
        self.assertIn("margin: 0.55rem 0 0;", derivation_block)
        self.assertIn("padding: 0;", case_block)
        self.assertIn("background: var(--reader-table-card-bg);", case_block)
        self.assertIn("font-size: 11px;", case_title_block)
        self.assertIn("background: var(--reader-table-card-bg);", case_stack_block)
        self.assertIn("font-size: 13px;", case_formula_block)
        self.assertIn("background: rgba(255, 255, 255, 0.92);", case_note_shell_block)
        self.assertIn("font-size: 12px;", case_note_block)

    def test_reference_layouts_for_split_and_r_factor_formulas_are_available(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        split_block = _rule_block(css, ".formula-group--split")
        divider_block = _rule_block(css, ".formula-split-divider")
        panel_block = _rule_block(css, ".formula-panel--r-factor")
        panel_row_block = _rule_block(css, ".formula-panel--r-factor .book-formula--panel-row")

        self.assertIn("grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);", split_block)
        self.assertIn("flex-direction: column;", divider_block)
        self.assertIn("border: 1px solid rgba(216, 221, 232, 0.96);", panel_block)
        self.assertIn("display: flex;", panel_row_block)
        self.assertIn("font-size: 14px;", panel_row_block)

    def test_mobile_sidebar_open_keeps_page_wrapper_unshifted(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        mobile_block_start = css.index("@media (max-width: 1080px) {")
        mobile_block_end = css.index("\n}\n\n@media (max-width: 760px) {", mobile_block_start)
        mobile_block = css[mobile_block_start:mobile_block_end]
        match = re.search(
            r"#mdbook-sidebar-toggle-anchor:checked ~ #mdbook-page-wrapper \{(?P<body>.*?)\n  \}",
            mobile_block,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Missing mobile page wrapper rule for open sidebar state")
        rule_body = match.group("body")

        self.assertIn("transform: none;", rule_body)
        self.assertIn("margin-left: 0;", rule_body)
        self.assertIn("margin-inline-start: 0;", rule_body)

    def test_mobile_sidebar_rows_keep_desktop_text_width_geometry(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        mobile_block_start = css.index("@media (max-width: 1080px) {")
        mobile_block_end = css.index("\n}\n\n@media (max-width: 760px) {", mobile_block_start)
        mobile_block = css[mobile_block_start:mobile_block_end]

        def mobile_rule(selector: str) -> str:
            match = re.search(
                rf"^[ \t]*{re.escape(selector)}\s*\{{(?P<body>.*?)^[ \t]*\}}",
                mobile_block,
                re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(match, f"Missing mobile CSS rule for {selector}")
            return match.group("body")

        row_block = mobile_rule(".reader-sidebar-row")
        reference_block = mobile_rule(".reader-sidebar-row--reference")
        front_matter_reference_block = mobile_rule(
            ".reader-sidebar-section--front-matter .reader-sidebar-row--reference"
        )
        icon_row_block = mobile_rule(".reader-sidebar-row--reference.reader-sidebar-row--with-icon")
        active_reference_block = mobile_rule(".reader-sidebar-row--reference.reader-sidebar-row--active")
        front_matter_active_reference_block = mobile_rule(
            ".reader-sidebar-section--front-matter .reader-sidebar-row--reference.reader-sidebar-row--active"
        )

        self.assertIn("grid-template-columns: 2.25rem minmax(0, 1fr);", row_block)
        self.assertIn("padding: 0.5rem 1.75rem 0.5rem 0.75rem;", row_block)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", reference_block)
        self.assertIn("padding: 0.4rem 1.25rem 0.4rem 0.75rem;", reference_block)
        self.assertIn(
            "padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);",
            front_matter_reference_block,
        )
        self.assertIn("grid-template-columns: 1.375rem minmax(0, 1fr);", icon_row_block)
        self.assertIn("gap: 0.5rem;", icon_row_block)
        self.assertIn("padding: 0.4rem 1.25rem 0.4rem 0.75rem;", active_reference_block)
        self.assertIn(
            "padding: 0.4rem 1.25rem 0.4rem calc(1.1875rem + 0.625rem);",
            front_matter_active_reference_block,
        )

    def test_sidebar_title_width_contract_is_explicit(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        projection_block = _rule_block(css, ".reader-sidebar-projection")
        section_block = _rule_block(css, ".reader-sidebar-section")
        body_block = _rule_block(css, ".reader-sidebar-section-body")
        row_block = _rule_block(css, ".reader-sidebar-row")
        title_block = _rule_block(css, ".reader-sidebar-row-title")

        self.assertIn("width: 100%;", projection_block)
        self.assertIn("box-sizing: border-box;", projection_block)
        self.assertIn("width: 100%;", section_block)
        self.assertIn("box-sizing: border-box;", section_block)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", section_block)
        self.assertIn("width: 100%;", body_block)
        self.assertIn("box-sizing: border-box;", body_block)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", body_block)
        self.assertIn("width: 100%;", row_block)
        self.assertIn("box-sizing: border-box;", row_block)
        self.assertIn("display: block;", title_block)
        self.assertIn("width: 100%;", title_block)

    def test_sidebar_open_state_restores_display_before_layout_work(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function installSidebarDisplayStateSync()", js)
        self.assertIn('const sidebar = document.getElementById("mdbook-sidebar");', js)
        self.assertIn('const sidebarToggle = document.getElementById("mdbook-sidebar-toggle-anchor");', js)
        self.assertIn("function syncSidebarDisplayState()", js)
        self.assertIn("if (!sidebarToggle.checked) {", js)
        self.assertIn('if (sidebar.style.display === "none") {', js)
        self.assertIn('sidebar.style.display = "";', js)
        self.assertIn("sidebar.offsetHeight;", js)
        self.assertIn('sidebar.setAttribute("aria-hidden", "false");', js)
        self.assertIn('requestAnimationFrame(syncSidebarDisplayState);', js)
        self.assertRegex(
            js,
            r'applyPageVariants\(\);\s+installSidebarDisplayStateSync\(\);\s+installSidebarShellGeometry\(\);',
        )

    def test_mobile_chapter_selector_is_removed(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertNotIn(".reader-mobile-chapter-bar {", css)
        self.assertNotIn(".reader-mobile-chapter-toggle {", css)
        self.assertNotIn(".reader-mobile-chapter-kicker {", css)
        self.assertNotIn(".reader-mobile-chapter-title {", css)
        self.assertNotIn("function installMobileChapterBar()", js)
        self.assertNotIn('document.querySelector(".reader-mobile-chapter-toggle")', js)


if __name__ == "__main__":
    unittest.main()
