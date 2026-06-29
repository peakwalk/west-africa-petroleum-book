from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
CUSTOM_CSS_PATH = ROOT_DIR / "theme/custom.css"
CUSTOM_JS_PATH = ROOT_DIR / "theme/custom.js"
INDEX_HBS_PATH = ROOT_DIR / "theme/index.hbs"
TEST_SITE_RENDER_PATH = ROOT_DIR / "scripts/test-site-render.sh"
READER_RUNTIME_CHECK_PATH = ROOT_DIR / "scripts/check_reader_runtime_outline.mjs"
BROWSERLESS_RUNTIME_BUILD_CONTRACT_PATH = ROOT_DIR / "scripts/check_reader_runtime_build_contract.mjs"
BROWSER_RUNTIME_CHECK_PATH = ROOT_DIR / "scripts/check_reader_runtime_browser.swift"
BROWSER_RUNTIME_CONFIG_PATH = ROOT_DIR / "scripts/build_reader_runtime_browser_check_config.mjs"
BROWSER_RUNTIME_SERVER_PATH = ROOT_DIR / "scripts/serve_reader_runtime_browser_check.py"
LOCALIZE_READER_SHELL_PATH = ROOT_DIR / "scripts/localize_reader_shell.mjs"
BOOK_PAGE_VARIANTS_PATH = ROOT_DIR / "scripts/shared/book-page-variants.mjs"
READER_OUTLINE_RUNTIME_PATH = ROOT_DIR / "scripts/shared/reader-outline-runtime.mjs"
EN_BOOK_TOML_PATH = ROOT_DIR / "editions/en/book.toml"
FR_BOOK_TOML_PATH = ROOT_DIR / "editions/fr/book.toml"


def _rule_block(css: str, selector: str) -> str:
    pattern = re.compile(rf"(?m)^[ \t]*{re.escape(selector)}\s*\{{(?P<body>.*?)\n\}}", re.DOTALL)
    match = pattern.search(css)
    if match is None:
        raise AssertionError(f"Missing CSS rule for {selector}")
    return match.group("body")


class ThemeCustomCssTest(unittest.TestCase):
    def test_book_tomls_load_theme_custom_js_without_vendored_panzoom(self) -> None:
        en_book_toml = EN_BOOK_TOML_PATH.read_text(encoding="utf-8")
        fr_book_toml = FR_BOOK_TOML_PATH.read_text(encoding="utf-8")

        self.assertIn('additional-js = ["theme/ga.js", "theme/custom.js"]', en_book_toml)
        self.assertIn('additional-js = ["theme/ga.js", "theme/custom.js"]', fr_book_toml)
        self.assertNotIn("theme/vendor/panzoom.min.js", en_book_toml)
        self.assertNotIn("theme/vendor/panzoom.min.js", fr_book_toml)

    def test_reader_figure_new_tab_contract_is_present_in_theme_sources(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function installFigureImageOpenLinks()", js)
        self.assertIn('document.querySelectorAll(".reader-article .figure-card img")', js)
        self.assertIn('window.open(imageUrl, "_blank", "noopener")', js)
        self.assertIn('event.key === "Enter" || event.key === " "', js)
        self.assertIn(".figure-card-image--zoom-link:focus-visible {", css)
        self.assertNotIn('window.Panzoom || window.panzoom', js)
        self.assertNotIn(".figure-viewer {", css)

    def test_reader_figure_new_tab_flow_removes_custom_viewer_fit_logic(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertNotIn("function syncImageBoundsToViewport()", js)
        self.assertNotIn("viewport.getBoundingClientRect()", js)
        self.assertNotIn("image.style.maxWidth =", js)
        self.assertNotIn("image.style.maxHeight =", js)
        self.assertNotIn('window.addEventListener("resize", handleViewerResize);', js)

    def test_book_page_variants_are_applied_at_build_time(self) -> None:
        hbs = INDEX_HBS_PATH.read_text(encoding="utf-8")
        localize_shell = LOCALIZE_READER_SHELL_PATH.read_text(encoding="utf-8")

        self.assertNotIn("window.bookPageVariants", hbs)
        self.assertNotIn("applyInitialBookPageVariant", hbs)
        self.assertIn('import { getBookPageBodyClasses } from "./shared/book-page-variants.mjs";', localize_shell)
        self.assertIn("function injectBodyClasses(html, pageKey) {", localize_shell)
        self.assertTrue(BOOK_PAGE_VARIANTS_PATH.exists())

    def test_runtime_page_variant_classifier_is_removed(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertNotIn("window.bookPageVariants", js)
        self.assertNotIn("function applyPageVariants() {", js)
        self.assertNotIn('document.body.classList.add("book-page-cover")', js)

    def test_reader_runtime_initializes_when_dom_is_already_ready(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function initializeReaderRuntime()", js)
        self.assertIn('if (document.readyState === "loading") {', js)
        self.assertIn('document.addEventListener("DOMContentLoaded", initializeReaderRuntime, { once: true });', js)
        self.assertIn("function scheduleReaderRuntimePass(callback)", js)
        self.assertIn("scheduleReaderRuntimePass(initializeReaderRuntime);", js)
        self.assertIn('window.setTimeout(function () {', js)
        self.assertNotIn("window.setTimeout(initializeReaderRuntime, 0);", js)

    def test_reader_runtime_exposes_hydration_state_without_infinite_bootstrap_spin(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function setReaderRuntimeState(state)", js)
        self.assertIn("window.__readerRuntimeState = state;", js)
        self.assertIn("document.documentElement.dataset.readerRuntimeState = state;", js)
        self.assertIn('setReaderRuntimeState("booting");', js)
        self.assertIn('setReaderRuntimeState("hydrating");', js)
        self.assertIn('setReaderRuntimeState("ready");', js)
        self.assertNotIn("if (!article || !sidebar) {\n      window.setTimeout(initializeReaderRuntime, 0);", js)

    def test_reader_runtime_retries_before_locking_initialized_state(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function scheduleReaderRuntimeRetry()", js)
        self.assertIn("scheduleReaderRuntimeRetry();", js)
        self.assertIn("runReaderRuntimeOutlinePass()", js)
        self.assertRegex(
            js,
            r"runReaderRuntimeOutlinePass\(\)\s*\.then\(function \(\) \{[\s\S]*?readerRuntimeInitialized = true;",
        )
        self.assertIn("installReaderRuntimeSidebarObserver(sidebar);", js)

    def test_reader_runtime_sidebar_observer_is_throttled_and_disconnects_after_stabilizing(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("let readerRuntimeSidebarObserver = null;", js)
        self.assertIn("let readerRuntimeSidebarRefreshQueued = false;", js)
        self.assertIn("function requestReaderRuntimeSidebarRefresh(sidebar)", js)
        self.assertIn("function installReaderRuntimeSidebarObserver(sidebar)", js)
        self.assertIn("readerRuntimeSidebarObserver.disconnect();", js)
        self.assertIn(
            'const outlineSource = sidebar.querySelector("mdbook-sidebar-scrollbox .chapter-item > .on-this-page");',
            js,
        )
        self.assertIn('const articleHasHeadings = Boolean(document.querySelector(".reader-article h2, .reader-article h3, .reader-article h4, .reader-article h5, .reader-article h6"));', js)
        self.assertIn("!articleHasHeadings || outlineSource || document.body.classList.contains(\"book-outline-ready\")", js)
        self.assertIn('attributeFilter: ["class", "hidden", "aria-hidden"]', js)

    def test_reader_runtime_defers_sidebar_refresh_until_initial_hydration_completes(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        observer_block = js[
            js.index("function installReaderRuntimeSidebarObserver(sidebar)"):
            js.index("function initializeReaderRuntime()", js.index("function installReaderRuntimeSidebarObserver(sidebar)"))
        ]
        observer_tail = observer_block[
            observer_block.index('readerRuntimeSidebarObserver.observe(scrollContainer, {'):
        ]

        self.assertIn("let readerRuntimeSidebarRefreshPending = false;", js)
        self.assertIn(
            "if (!readerRuntimeInitialized) {\n      readerRuntimeSidebarRefreshPending = true;\n      return;\n    }",
            js,
        )
        self.assertNotIn("requestReaderRuntimeSidebarRefresh(sidebar);", observer_tail)
        self.assertRegex(
            js,
            r"readerRuntimeInitialized = true;\s*if \(readerRuntimeSidebarRefreshPending\) \{\s*readerRuntimeSidebarRefreshPending = false;\s*requestReaderRuntimeSidebarRefresh\(sidebar\);",
        )

    def test_reader_runtime_sidebar_refresh_is_single_flight(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("let readerRuntimeSidebarRefreshInFlight = false;", js)
        self.assertIn("readerRuntimeSidebarRefreshInFlight = true;", js)
        self.assertRegex(
            js,
            r"\.finally\(function \(\) \{\s*readerRuntimeSidebarRefreshInFlight = false;[\s\S]*requestReaderRuntimeSidebarRefresh\(sidebar\);",
        )

    def test_runtime_binding_markers_are_written_after_successful_setup(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        search_bound_index = js.index('searchWrap.dataset.readerSearchSlotBound = "true";')
        self.assertLess(
            js.index('observer.observe(searchWrap, { attributes: true, attributeFilter: ["class"] });'),
            search_bound_index,
        )
        pagination_bound_index = js.rindex('pagination.dataset.readerPaginationHeightBound = "true";')
        self.assertLess(
            js.index('window.addEventListener("load", requestSync, { once: true });'),
            pagination_bound_index,
        )

    def test_figure_annotation_supports_alt_derived_caption_fallback(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("const figureCaptionRuntime = (function createFigureCaptionRuntime() {", js)
        self.assertIn("function parseFigureNumber(text) {", js)
        self.assertIn("function isLikelyAltDerivedCaption(text) {", js)
        self.assertIn("function buildAltDerivedFigureCaption(paragraph) {", js)
        self.assertIn('return parseFigureNumber(image.getAttribute("alt") || "");', js)
        self.assertIn(
            "const altDerivedCaption = figureCaptionRuntime.buildAltDerivedFigureCaption(paragraph);",
            js,
        )
        self.assertNotIn(r'/[.!?]["\']?$/.test(normalized)', js)

    def test_site_render_uses_shared_runtime_outline_checker(self) -> None:
        script = TEST_SITE_RENDER_PATH.read_text(encoding="utf-8")
        runtime_checker = READER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")

        self.assertTrue(READER_RUNTIME_CHECK_PATH.exists())
        self.assertTrue(READER_OUTLINE_RUNTIME_PATH.exists())
        self.assertIn("node scripts/check_reader_runtime_outline.mjs", script)
        self.assertIn('from "./shared/book-page-variants.mjs";', runtime_checker)
        self.assertIn('from "./shared/reader-outline-runtime.mjs";', runtime_checker)
        self.assertIn("countRuntimeFigures", runtime_checker)
        self.assertIn("countRuntimeFormulas", runtime_checker)
        self.assertIn("countRuntimeTables", runtime_checker)
        self.assertIn("collectRuntimeFigureNumbers", runtime_checker)
        self.assertIn("figureSentinels", runtime_checker)
        self.assertNotIn('import vm from "node:vm";', runtime_checker)
        self.assertNotIn("extractIifeExpression(", runtime_checker)

    def test_site_render_runs_cross_platform_reader_runtime_build_contract_check(self) -> None:
        script = TEST_SITE_RENDER_PATH.read_text(encoding="utf-8")

        self.assertTrue(BROWSERLESS_RUNTIME_BUILD_CONTRACT_PATH.exists())
        build_contract_checker = BROWSERLESS_RUNTIME_BUILD_CONTRACT_PATH.read_text(
            encoding="utf-8"
        )

        self.assertIn("node scripts/check_reader_runtime_build_contract.mjs", script)
        self.assertIn('from "./shared/book-page-variants.mjs";', build_contract_checker)
        self.assertIn("book-layout-booting", build_contract_checker)
        self.assertIn("book-outline-empty", build_contract_checker)
        self.assertIn("readerRuntimeSidebarRefreshInFlight", build_contract_checker)

    def test_build_contract_checker_rejects_unexpected_variant_classes_globally(self) -> None:
        build_contract_checker = BROWSERLESS_RUNTIME_BUILD_CONTRACT_PATH.read_text(
            encoding="utf-8"
        )
        page_variants = BOOK_PAGE_VARIANTS_PATH.read_text(encoding="utf-8")

        self.assertIn("bookPageVariantClassNames", build_contract_checker)
        self.assertIn('from "./shared/book-page-variants.mjs";', build_contract_checker)
        self.assertNotIn("const trackedVariantClasses = [", build_contract_checker)
        self.assertIn("export const bookPageVariantClassNames", page_variants)
        self.assertIn("const expectedClasses = new Set(getBookPageBodyClasses(pageKey, locale));", build_contract_checker)
        self.assertIn("if (!expectedClasses.has(className)) {", build_contract_checker)
        self.assertIn("assertLacksClass(bodyClasses, className, pageLabel);", build_contract_checker)

    def test_static_runtime_outline_checker_does_not_reject_empty_non_preserved_pages(self) -> None:
        runtime_checker = READER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")

        self.assertNotIn(
            "Unexpected runtime-empty outline page without preserved rail",
            runtime_checker,
        )

    def test_static_runtime_outline_checker_matches_reader_article_by_class_token(self) -> None:
        runtime_checker = READER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")

        self.assertIn(r'class="[^"]*\breader-article\b[^"]*"', runtime_checker)
        self.assertNotIn('<article class="reader-article"', runtime_checker)

    def test_site_render_runs_optional_browser_runtime_dom_check_on_macos(self) -> None:
        script = TEST_SITE_RENDER_PATH.read_text(encoding="utf-8")

        self.assertTrue(BROWSER_RUNTIME_CHECK_PATH.exists())
        self.assertTrue(BROWSER_RUNTIME_CONFIG_PATH.exists())
        self.assertTrue(BROWSER_RUNTIME_SERVER_PATH.exists())
        browser_checker = BROWSER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")
        browser_checker_config = BROWSER_RUNTIME_CONFIG_PATH.read_text(encoding="utf-8")
        browser_runtime_server = BROWSER_RUNTIME_SERVER_PATH.read_text(encoding="utf-8")

        self.assertIn("run_browser_runtime_check_if_available()", script)
        self.assertIn('if [ "$(uname -s)" = "Darwin" ] && command -v swift >/dev/null 2>&1; then', script)
        self.assertIn("node scripts/build_reader_runtime_browser_check_config.mjs", script)
        self.assertIn("scripts/serve_reader_runtime_browser_check.py", script)
        self.assertIn('browser_server_port_file="$(create_temp_file "reader-runtime-browser-port." ".txt")"', script)
        self.assertIn('browser_port="$(cat "$browser_server_port_file")"', script)
        self.assertNotIn("python3 -m http.server", script)
        self.assertNotIn('sock.bind(("127.0.0.1", 0))', script)
        self.assertIn("127.0.0.1", script)
        self.assertIn("--base-url", script)
        self.assertIn("--page-config", script)
        self.assertIn("--scope", script)
        self.assertIn('browser_check_scope="${READER_RUNTIME_BROWSER_CHECK_SCOPE:-smoke}"', script)
        self.assertIn("swift scripts/check_reader_runtime_browser.swift", script)
        self.assertIn("Skipping browser runtime DOM check", script)
        self.assertLess(
            script.index("node scripts/check_reader_runtime_outline.mjs"),
            script.rindex("\nrun_browser_runtime_check_if_available\n"),
        )
        self.assertIn("import WebKit", browser_checker)
        self.assertIn("loadFileURL", browser_checker)
        self.assertIn("evaluateJavaScript", browser_checker)
        self.assertNotIn("window.requestAnimationFrame = function", browser_checker)
        self.assertIn("readerRuntimeState", browser_checker)
        self.assertIn('case "--scope":', browser_checker)
        self.assertIn('if config.scope == "full"', browser_checker)
        self.assertIn('from "./shared/book-page-variants.mjs";', browser_checker_config)
        self.assertIn("getPreserveOutlinePaths", browser_checker_config)
        self.assertIn("ThreadingHTTPServer", browser_runtime_server)
        self.assertIn("SimpleHTTPRequestHandler", browser_runtime_server)
        self.assertIn("--port-file", browser_runtime_server)
        self.assertIn("serve_forever()", browser_runtime_server)

    def test_site_render_uses_portable_tempfiles_for_browser_runtime_check(self) -> None:
        script = TEST_SITE_RENDER_PATH.read_text(encoding="utf-8")

        self.assertNotIn('mktemp "${TMPDIR:-/tmp}/reader-runtime-browser-config.XXXXXX.json"', script)
        self.assertNotIn('mktemp "${TMPDIR:-/tmp}/reader-runtime-browser-http.XXXXXX.log"', script)
        self.assertNotIn('mktemp "${TMPDIR:-/tmp}/reader-runtime-browser-port.XXXXXX.txt"', script)
        self.assertIn("tempfile.mkstemp", script)

    def test_browser_runtime_smoke_config_covers_high_risk_outline_pages(self) -> None:
        browser_checker_config = BROWSER_RUNTIME_CONFIG_PATH.read_text(encoding="utf-8")

        self.assertIn("chapter-09-socio-political-determinants.html", browser_checker_config)
        self.assertIn("chapter-11-general-conclusion.html", browser_checker_config)
        self.assertIn("chapter-05-key-socio-political-determinants-of-oil-sector-performance.html", browser_checker_config)
        self.assertIn('"chapters/general-conclusion.html"', browser_checker_config)

    def test_browser_runtime_checker_respects_reader_page_meta_reference_sections(self) -> None:
        browser_checker = BROWSER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")

        self.assertIn("struct ReferenceSections: Decodable {", browser_checker)
        self.assertIn("struct ReaderPageMeta: Decodable {", browser_checker)
        self.assertIn("let referenceSections: ReferenceSections?", browser_checker)
        self.assertIn("func loadReaderPageMeta(bookRoot: URL) throws -> [String: ReaderPageMeta]", browser_checker)
        self.assertIn("let figuresEnabled = pageMeta?.referenceSections?.figures != false", browser_checker)
        self.assertIn("let tablesEnabled = pageMeta?.referenceSections?.tables != false", browser_checker)
        self.assertIn("let formulasEnabled = pageMeta?.referenceSections?.formulas != false", browser_checker)

    def test_browser_runtime_checker_ignores_expected_webkit_navigation_cancellations(self) -> None:
        browser_checker = BROWSER_RUNTIME_CHECK_PATH.read_text(encoding="utf-8")

        self.assertIn("NSURLErrorCancelled", browser_checker)
        self.assertIn(
            "nsError.domain == NSURLErrorDomain && nsError.code == NSURLErrorCancelled",
            browser_checker,
        )

    def test_site_render_formula_coverage_is_optional_without_docx_resources(self) -> None:
        script = TEST_SITE_RENDER_PATH.read_text(encoding="utf-8")

        self.assertIn("run_docx_formula_check_if_available()", script)
        self.assertIn('if [ -f "$docx_path" ]; then', script)
        self.assertIn("python3 scripts/check_docx_formula_coverage.py --edition \"$edition\"", script)
        self.assertIn("Skipping DOCX formula coverage check", script)
        self.assertIn("run_docx_formula_check_if_available en", script)
        self.assertIn("run_docx_formula_check_if_available fr", script)

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

    def test_figure_annotation_accepts_colonless_and_french_caption_spacing(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function parseFigureCaption(text)", js)
        self.assertIn("function isNarrativeFigureReference(text)", js)
        self.assertIn("if (isNarrativeFigureReference(normalized))", js)
        self.assertIn(r'/^Figure\s+0*(\d+)(?:\s*:\s*|\s+)(.*)$/i', js)
        self.assertIn('number: String(Number(match[1]))', js)
        self.assertIn(
            "const explicitCaption = figureCaptionRuntime.parseFigureCaption(paragraph.textContent || \"\");",
            js,
        )
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
        self.assertIn(r'/^(?:Table|Tableau)\s+(\d+)(?:\s*:\s*|\s+)(.*)$/i', js)
        self.assertIn('document.documentElement.lang || "en"', js)
        self.assertIn("function normalizeDocxTableStructure(table)", js)
        self.assertIn('table.classList.contains("t1")', js)
        self.assertIn("table.createTHead()", js)

    def test_mobile_reader_keeps_language_switch_in_toolbar_before_search(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        sidebar_switch_block = _rule_block(css, '.reader-language-switch[data-reader-language-switch="sidebar"]')
        marker = "@media (max-width: 1023px) {"
        start = css.index(marker)
        next_marker = css.index("\n\n@media", start + len(marker))
        block = css[start:next_marker]

        self.assertIn("display: none;", sidebar_switch_block)
        self.assertIn("min-width: 0;", block)
        self.assertIn("padding-inline-start: 0.5rem;", block)
        self.assertIn("padding-inline-end: 0;", block)
        self.assertIn("gap: 0.5rem;", block)
        self.assertIn(
            '.toolbar-actions .reader-language-switch[data-reader-language-switch="toolbar"] {',
            block,
        )
        self.assertIn("display: inline-flex;", block)
        self.assertIn("#mdbook-search-toggle {", block)
        self.assertIn("display: inline-flex !important;", block)

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

    def test_reader_cross_reference_linker_supports_figures_tables_sections_chapters_and_equations(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("function installCrossReferenceLinks()", js)
        self.assertIn('document.querySelectorAll(".reader-article p, .reader-article li")', js)
        self.assertIn(
            '.reader-article h1[id], .reader-article h2[id], .reader-article h3[id], .reader-article h4[id], .reader-article h5[id], .reader-article h6[id]',
            js,
        )
        self.assertIn('document.querySelectorAll(".reader-sidebar-row--chapter[href]")', js)
        self.assertIn('document.getElementById("figure-" + referenceNumber)', js)
        self.assertIn('document.getElementById("table-" + referenceNumber)', js)
        self.assertIn('document.getElementById("formula-" + formulaAnchorLabel)', js)
        self.assertIn('element.closest("a, h1, h2, h3, h4, h5, h6")', js)
        self.assertIn('element.closest(".figure-card, .table-anchor-target, .formula-anchor-target, .reference-index")', js)
        self.assertIn('textNode.parentElement.closest("a")', js)
        self.assertIn(
            r'/\b(Figure)\s+(\d+)\b|\b(Table|Tableau)\s+(\d+)\b|\b(Section)\s+(\d+(?:\.\d+)*)\b|\b(Chapter|Chapitre)\s+(\d+)\b|\b(Equation|Formula|Équation|Formule)\s+(\d+(?:\.\d+)*)\b/g',
            js,
        )
        self.assertIn('installCrossReferenceLinks();', js)

    def test_outline_reference_sections_are_gated_by_reader_page_meta(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("const referenceSections = pageMeta && pageMeta.referenceSections ? pageMeta.referenceSections : null;", js)
        self.assertIn("const figuresEnabled = !referenceSections || referenceSections.figures !== false;", js)
        self.assertIn("const tablesEnabled = !referenceSections || referenceSections.tables !== false;", js)
        self.assertIn("const formulasEnabled = !referenceSections || referenceSections.formulas !== false;", js)
        self.assertIn("populateOutlineSection(figuresSection, figureItems, figuresEnabled);", js)
        self.assertIn("populateOutlineSection(tablesSection, tableItems, tablesEnabled);", js)
        self.assertIn("populateOutlineSection(formulasSection, formulaItems, formulasEnabled);", js)
        self.assertIn("function runReaderRuntimeOutlinePass()", js)
        self.assertIn("return Promise.resolve(installOutlineReferenceSections())", js)
        self.assertIn("syncOutlineRailVisibility();", js)

    def test_hidden_outline_sections_stay_hidden(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".book-outline-section[hidden]")

        self.assertIn("display: none;", block)

    def test_mobile_outline_card_uses_stable_grid_navigation(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        list_block = _rule_block(css, ".reader-mobile-outline-card .on-this-page > ol")
        item_block = _rule_block(css, ".reader-mobile-outline-card .on-this-page li.header-item")
        separator_block = _rule_block(
            css,
            ".reader-mobile-outline-card .on-this-page li.header-item:not(:last-child)::after",
        )
        wrapper_block = _rule_block(
            css,
            ".reader-mobile-outline-card .on-this-page .chapter-link-wrapper",
        )
        link_block_match = re.search(
            r"\.reader-mobile-outline-card \.on-this-page a,\n"
            r"\.reader-mobile-outline-card \.on-this-page a:visited \{(?P<body>.*?)\n\}",
            css,
            re.DOTALL,
        )

        self.assertIn("display: grid;", list_block)
        self.assertIn(
            "grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr));",
            list_block,
        )
        self.assertNotIn("flex-wrap:", list_block)
        self.assertIn("display: block;", item_block)
        self.assertIn("content: none;", separator_block)
        self.assertIn("display: none;", separator_block)
        self.assertIn("width: 100%;", wrapper_block)
        self.assertIsNotNone(link_block_match)
        link_block = link_block_match.group("body")
        self.assertIn("display: block;", link_block)
        self.assertIn("overflow-wrap: break-word;", link_block)

    def test_outline_reference_titles_wrap_without_truncation(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")
        block = _rule_block(css, ".reader-outline .book-outline-link--reference-title")

        self.assertIn("white-space: normal;", block)
        self.assertNotIn("overflow: hidden;", block)
        self.assertNotIn("display: -webkit-box;", block)
        self.assertNotIn("-webkit-line-clamp:", block)
        self.assertNotIn("const conciseText = truncateReferenceText(primaryClause || normalizedText, 44);", js)

    def test_outline_reference_titles_preserve_leading_articles_and_symbols(self) -> None:
        js = CUSTOM_JS_PATH.read_text(encoding="utf-8")

        self.assertIn("const normalizedText = normalizeText(text);", js)
        self.assertNotIn('replace(/^[a-z](?:\\s+and\\s+[a-z])?\\s+/i, "")', js)

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

    def test_table_12_h_factor_formula_can_wrap_within_the_cell(self) -> None:
        css = CUSTOM_CSS_PATH.read_text(encoding="utf-8")

        formula_block = _rule_block(css, "#table-12 .table-12-h-factor-cell > .book-formula")
        line_block = _rule_block(
            css,
            "#table-12 .table-12-h-factor-cell > .book-formula .book-formula-line",
        )

        self.assertIn("width: 100%;", formula_block)
        self.assertIn("max-width: none;", formula_block)
        self.assertIn("overflow-x: visible;", formula_block)
        self.assertIn("white-space: normal;", formula_block)
        self.assertNotIn("width: max-content;", formula_block)
        self.assertIn("width: 100%;", line_block)
        self.assertIn("min-width: 0;", line_block)
        self.assertIn("white-space: normal;", line_block)

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
        self.assertIn("padding: 0.5rem 2.125rem 0.5rem 0.75rem;", row_block)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", reference_block)
        self.assertIn("padding: 0.4rem 2.125rem 0.4rem 0.75rem;", reference_block)
        self.assertIn(
            "padding: 0.4rem 2.125rem 0.4rem calc(1.1875rem + 0.625rem);",
            front_matter_reference_block,
        )
        self.assertIn("grid-template-columns: 1.375rem minmax(0, 1fr);", icon_row_block)
        self.assertIn("gap: 0.5rem;", icon_row_block)
        self.assertIn("padding: 0.4rem 2.125rem 0.4rem 0.75rem;", active_reference_block)
        self.assertIn(
            "padding: 0.4rem 2.125rem 0.4rem calc(1.1875rem + 0.625rem);",
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
            r'installSidebarDisplayStateSync\(\);\s+hydrateSidebarProjectionRows\(projection\);',
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
