from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class BookEditionBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["npm", "run", "build:site"],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(ROOT_DIR / "public", ignore_errors=True)

    @staticmethod
    def _extract_title(html: str) -> str:
        match = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
        if match is None:
            raise AssertionError("Expected a <title> tag in generated HTML.")
        return match.group(1).strip()

    @staticmethod
    def _extract_meta_description(html: str) -> str:
        match = re.search(r'<meta name="description" content="([^"]*)">', html)
        if match is None:
            raise AssertionError('Expected a meta name="description" tag in generated HTML.')
        return match.group(1).strip()

    @staticmethod
    def _extract_meta_content(html: str, name: str) -> str | None:
        match = re.search(
            rf'<meta name="{re.escape(name)}" content="([^"]*)">',
            html,
        )
        return match.group(1).strip() if match is not None else None

    @staticmethod
    def _extract_link_href(html: str, rel: str, hreflang: str | None = None) -> str | None:
        attributes = [f'rel="{rel}"']
        if hreflang is not None:
            attributes.append(f'hreflang="{hreflang}"')
        pattern = "<link " + r"[^>]*".join(attributes) + r'[^>]*href="([^"]+)"'
        match = re.search(pattern, html)
        return match.group(1) if match is not None else None

    @staticmethod
    def _extract_json_ld_blocks(html: str) -> list[object]:
        blocks = []
        for raw_json in re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            html,
            re.DOTALL,
        ):
            blocks.append(json.loads(raw_json))
        return blocks

    @staticmethod
    def _iter_canonical_book_pages(locale_root: Path) -> list[Path]:
        pages = [locale_root / "index.html"]
        pages.extend(
            sorted(
                chapter_path
                for chapter_path in (locale_root / "chapters").glob("*.html")
                if chapter_path.name not in {"front-matter.html", "cover.html"}
            )
        )
        return pages

    def test_dual_book_outputs_are_published(self) -> None:
        self.assertTrue((ROOT_DIR / "public" / "book" / "index.html").exists())
        self.assertTrue((ROOT_DIR / "public" / "fr" / "book" / "index.html").exists())

    def test_book_header_exposes_cross_edition_switch(self) -> None:
        english_disclaimer = (
            ROOT_DIR / "public" / "book" / "chapters" / "disclaimer.html"
        ).read_text(encoding="utf-8")
        english_foreword = (
            ROOT_DIR / "public" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")
        english_french_edition_foreword = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "foreword-to-the-french-edition.html"
        ).read_text(encoding="utf-8")
        english_value_chain = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")
        french_foreword = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")
        french_value_chain = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")

        self.assertIn('class="reader-language-switch"', english_disclaimer)
        self.assertIn('/fr/book/?lang=fr', english_disclaimer)
        self.assertIn('class="reader-language-switch"', english_foreword)
        self.assertIn('/fr/book/?lang=fr', english_foreword)
        self.assertIn('class="reader-language-switch"', english_french_edition_foreword)
        self.assertIn(
            '/fr/book/chapters/foreword.html?lang=fr',
            english_french_edition_foreword,
        )
        self.assertIn('class="reader-language-switch"', french_foreword)
        self.assertIn(
            '/book/chapters/foreword-to-the-french-edition.html?lang=en',
            french_foreword,
        )
        self.assertIn(
            '/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html?lang=fr',
            english_value_chain,
        )
        self.assertIn(
            '/book/chapters/chapter-05-hydrocarbon-value-chain.html?lang=en',
            french_value_chain,
        )

    def test_book_header_language_switch_keeps_en_then_fr_order_without_label(self) -> None:
        english_disclaimer = (
            ROOT_DIR / "public" / "book" / "chapters" / "disclaimer.html"
        ).read_text(encoding="utf-8")
        french_foreword = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")

        self.assertNotIn('class="reader-language-label"', english_disclaimer)
        self.assertNotIn('class="reader-language-label"', french_foreword)

        self.assertRegex(
            english_disclaimer,
            re.compile(
                r'<nav class="reader-language-switch"[^>]*>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">EN</span>\s*'
                r'<a class="reader-language-option" href="/fr/book/\?lang=fr" lang="fr" hreflang="fr">FR</a>\s*'
                r'</nav>'
            ),
        )
        self.assertRegex(
            french_foreword,
            re.compile(
                r'<nav class="reader-language-switch"[^>]*>\s*'
                r'<a class="reader-language-option" href="/book/chapters/foreword-to-the-french-edition\.html\?lang=en" lang="en" hreflang="en">EN</a>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">FR</span>\s*'
                r'</nav>'
            ),
        )

    def test_book_reader_injects_toolbar_and_sidebar_language_switches(self) -> None:
        english_disclaimer = (
            ROOT_DIR / "public" / "book" / "chapters" / "disclaimer.html"
        ).read_text(encoding="utf-8")
        french_foreword = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            english_disclaimer,
            re.compile(
                r'<div class="book-sidebar-intro">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="sidebar"[^>]*>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">EN</span>\s*'
                r'<a class="reader-language-option" href="/fr/book/\?lang=fr" lang="fr" hreflang="fr">FR</a>\s*'
                r'</nav>\s*'
                r'<p class="book-sidebar-book-title">',
                re.DOTALL,
            ),
        )
        self.assertRegex(
            english_disclaimer,
            re.compile(
                r'<div class="toolbar-actions">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="toolbar"[^>]*>',
                re.DOTALL,
            ),
        )
        self.assertRegex(
            french_foreword,
            re.compile(
                r'<div class="book-sidebar-intro">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="sidebar"[^>]*>\s*'
                r'<a class="reader-language-option" href="/book/chapters/foreword-to-the-french-edition\.html\?lang=en" lang="en" hreflang="en">EN</a>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">FR</span>\s*'
                r'</nav>\s*'
                r'<p class="book-sidebar-book-title">',
                re.DOTALL,
            ),
        )

    def test_french_book_cover_uses_french_entry_copy(self) -> None:
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("Édition de référence Upstream Atlas", french_book_index)
        self.assertIn("Commencer la lecture", french_book_index)

    def test_english_book_cover_uses_english_cover_asset(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('src="images/figure-000.webp"', english_book_index)
        self.assertNotIn('src="images/figure-001.webp"', english_book_index)

    def test_french_book_cover_uses_french_cover_asset(self) -> None:
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('src="images/figure-000.webp"', french_book_index)
        self.assertNotIn('src="images/figure-001.webp"', french_book_index)

    def test_french_front_matter_and_chapter_titles_use_french_copy(self) -> None:
        french_figures = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "list-of-figures.html"
        ).read_text(encoding="utf-8")
        french_foreword = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")
        french_intro = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "general-introduction.html"
        ).read_text(encoding="utf-8")
        french_chapter_one = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Liste des figures", french_figures)
        self.assertIn("Chapitre 1 : Chaîne des valeurs du secteur des hydrocarbures", french_figures)
        self.assertNotIn("List of Figures", french_figures)
        self.assertIn("Avant-propos", french_foreword)
        self.assertIn("Les ressources géo-extractives constituent une source de revenus", french_foreword)
        self.assertNotIn("Foreword", french_foreword)
        self.assertIn("Introduction générale", french_intro)
        self.assertIn("Formés dans le sous-sol", french_intro)
        self.assertIn("Chapitre 1 : Chaîne des valeurs du secteur des hydrocarbures", french_chapter_one)
        self.assertNotIn("Chapter 1: Value Chain of the Hydrocarbon Sector", french_chapter_one)

    def test_english_front_matter_includes_foreword_to_the_french_edition(self) -> None:
        english_french_edition_foreword = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "foreword-to-the-french-edition.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Foreword to the French Edition", english_french_edition_foreword)
        self.assertIn(
            "Geo-extractive resources constitute an important source of revenue for countries endowed with them",
            english_french_edition_foreword,
        )
        self.assertIn("Petroleum as a Driver of Socio-Economic Development", english_french_edition_foreword)
        self.assertIn("<strong>Charles</strong><br />", english_french_edition_foreword)

    def test_french_chapter_one_table_one_uses_superscript_notes_like_english_table_card(self) -> None:
        french_chapter_one = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")
        visible_chapter_one = re.sub(r"<!--.*?-->", "", french_chapter_one, flags=re.DOTALL)
        normalized_visible_chapter_one = re.sub(r"\s+", " ", visible_chapter_one)

        self.assertIn("30.031<sup>1</sup>", french_chapter_one)
        self.assertIn("202.000<sup>1</sup>", french_chapter_one)
        self.assertIn("645 (estimation)<sup>2</sup>", french_chapter_one)
        self.assertIn("9 000 (estimation)<sup>2</sup>", french_chapter_one)
        self.assertIn("<p><sup>1</sup> Données des ministères</p>", normalized_visible_chapter_one)
        self.assertIn("<p><sup>2</sup> Rapport de RPS Energy, 2006</p>", normalized_visible_chapter_one)
        self.assertNotIn("30.031*", french_chapter_one)
        self.assertNotIn("202.000*", french_chapter_one)
        self.assertNotIn("645 (estimation)**", french_chapter_one)
        self.assertNotIn("9 000 (estimation)**", french_chapter_one)

    def test_french_chapter_one_figure_two_keeps_dual_image_structure_outside_the_preceding_list(self) -> None:
        french_chapter_one = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            french_chapter_one,
            re.compile(
                r"</ul>\s*"
                r"<p><img src=\"\.\./images/figure-002-a\.webp\"[^>]*></p>\s*"
                r"<p><img src=\"\.\./images/figure-002-b\.webp\"[^>]*></p>\s*"
                r"<p>Figure 2:",
                re.DOTALL,
            ),
        )

    def test_french_chapter_one_figure_four_uses_french_pdf_rendered_asset(self) -> None:
        french_chapter_one = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-004.webp"', french_chapter_one)
        self.assertNotIn('src="../images/figure-004.png"', french_chapter_one)
        self.assertNotIn('src="../images/figure-004-oil-cuts-transparent.webp"', french_chapter_one)

    def test_french_chapter_two_and_three_use_french_figure_asset_targets(self) -> None:
        french_chapter_two = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html"
        ).read_text(encoding="utf-8")
        french_chapter_three = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-03-tax-regimes-in-the-petroleum-sector.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-005.webp"', french_chapter_two)
        self.assertIn('src="../images/figure-006.webp"', french_chapter_two)
        self.assertIn('src="../images/figure-008.webp"', french_chapter_two)
        self.assertIn('src="../images/figure-009.webp"', french_chapter_two)
        self.assertIn('src="../images/figure-019.webp"', french_chapter_two)
        self.assertNotIn('src="../images/figure-005-upstream-phases-transparent.webp"', french_chapter_two)
        self.assertNotIn('src="../images/figure-006-block-assignment-transparent.webp"', french_chapter_two)
        self.assertNotIn('src="../images/figure-005.png"', french_chapter_two)
        self.assertNotIn('src="../images/figure-006.png"', french_chapter_two)
        self.assertNotIn('src="../images/figure-008.png"', french_chapter_two)
        self.assertNotIn('src="../images/figure-009.png"', french_chapter_two)
        self.assertNotIn('src="../images/figure-009.jpg"', french_chapter_two)
        self.assertNotIn('src="../images/figure-019.svg"', french_chapter_two)

        self.assertIn('src="../images/figure-022.webp"', french_chapter_three)
        self.assertNotIn('src="../images/figure-022.svg"', french_chapter_three)

    def test_english_chapter_five_figure_nine_uses_replacement_webp_asset(self) -> None:
        english_chapter_five = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-009.webp"', english_chapter_five)
        self.assertNotIn('src="../images/figure-009.png"', english_chapter_five)
        self.assertNotIn('src="../images/figure-009.jpg"', english_chapter_five)

    def test_english_chapter_five_figure_ten_uses_replacement_webp_asset(self) -> None:
        english_chapter_five = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-010.webp"', english_chapter_five)
        self.assertNotIn('src="../images/figure-010.png"', english_chapter_five)

    def test_english_chapter_five_figure_eleven_published_webp_is_non_empty(self) -> None:
        english_chapter_five = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")
        published_figure_eleven = ROOT_DIR / "public" / "book" / "images" / "figure-011.webp"

        self.assertIn('src="../images/figure-011.webp"', english_chapter_five)
        self.assertTrue(published_figure_eleven.exists())
        self.assertGreater(
            published_figure_eleven.stat().st_size,
            0,
            "Expected the published Figure 11 WebP asset to be non-empty.",
        )

    def test_english_chapter_five_rehydrates_table_two_and_three_from_replacement_docx(self) -> None:
        english_chapter_five = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")

        self.assertIn("<table>", english_chapter_five)
        self.assertIn("Table 2 Estimated Hydrocarbon Resources in West Africa", english_chapter_five)
        self.assertIn("Crude Oil Reserves (MMbbl)", english_chapter_five)
        self.assertIn("30,031*", english_chapter_five)
        self.assertIn("Table 3 Daily Oil Production by Country (Trading Economics, 2025)", english_chapter_five)
        self.assertIn("Reference Period", english_chapter_five)
        self.assertIn("Mbbl/d", english_chapter_five)

    def test_english_chapter_six_figure_twenty_one_keeps_one_image_and_body_copy(self) -> None:
        english_chapter_six = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-06-upstream-operations-and-government-roles.html"
        ).read_text(encoding="utf-8")

        self.assertEqual(english_chapter_six.count('src="../images/figure-021.webp"'), 1)
        self.assertIn(
            "<p>Figure 21 illustrates the typical workflow used to transform raw seismic data into drilling decisions.",
            english_chapter_six,
        )
        self.assertIn(
            "<p>Figure 21 Workflow from Seismic Acquisition and Interpretation to Prospect Evaluation and Well Planning.</p>",
            english_chapter_six,
        )

    def test_english_figure_body_copy_does_not_duplicate_figure_cards(self) -> None:
        english_chapter_six = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-06-upstream-operations-and-government-roles.html"
        ).read_text(encoding="utf-8")
        english_chapter_seven = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-07-petroleum-fiscal-regimes.html"
        ).read_text(encoding="utf-8")
        english_chapter_eight = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-08-west-african-fiscal-regimes.html"
        ).read_text(encoding="utf-8")

        for asset in ["016", "025", "026", "027", "038", "040", "041", "042"]:
            self.assertEqual(english_chapter_six.count(f'src="../images/figure-{asset}.webp"'), 1)

        for asset in ["069", "070"]:
            self.assertEqual(english_chapter_seven.count(f'src="../images/figure-{asset}.webp"'), 1)

        self.assertEqual(english_chapter_eight.count('src="../images/figure-072.webp"'), 1)

        self.assertIn(
            "<p>Figure 16 shows the process for the award of petroleum blocks to International Oil Companies (IOCs) for exploration and production activities.</p>",
            english_chapter_six,
        )
        self.assertIn(
            "<p>Figure 38 and Figure 39 illustrate the importance of preserving geological samples and subsurface data acquired during petroleum exploration and development activities.",
            english_chapter_six,
        )
        self.assertIn(
            "<p>Figure 69 illustrates the typical distribution of revenues generated from petroleum production under a fiscal regime.",
            english_chapter_seven,
        )
        self.assertIn(
            "Figure 72, Figure 73, Figure 74, Figure 75, Figure 76, and Figure 77 present simplified illustrations of State-Contractor revenue sharing under the petroleum fiscal regimes",
            english_chapter_eight,
        )

    def test_english_chapter_four_table_one_caption_excludes_list_of_tables_page_number(self) -> None:
        english_chapter_four = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-04-national-oil-companies-in-west-africa.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Table 1 Overview of National Oil Companies in West Africa", english_chapter_four)
        self.assertNotIn("Table 1 Overview of National Oil Companies in West Africa 175", english_chapter_four)

    def test_english_chapter_eight_rehydrates_principal_fiscal_tables(self) -> None:
        english_chapter_eight = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-08-west-african-fiscal-regimes.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Table 20 Principal Fiscal Elements", english_chapter_eight)
        self.assertIn("Senegal", english_chapter_eight)
        self.assertIn("Table 33 Overview of Fiscal Systems", english_chapter_eight)
        self.assertIn("<table>", english_chapter_eight)
        self.assertIn("<thead>", english_chapter_eight)
        self.assertIn("<tbody>", english_chapter_eight)
        self.assertNotIn("&amp;amp;", english_chapter_eight)

    def test_french_chapter_two_figure_ten_uses_full_webp_asset(self) -> None:
        french_chapter_two = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-010.webp"', french_chapter_two)
        self.assertNotIn('src="../images/figure-010.png"', french_chapter_two)

    def test_french_body_chapters_do_not_leak_english_placeholder_copy(self) -> None:
        chapter_four = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html"
        ).read_text(encoding="utf-8")
        chapter_five = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-05-key-socio-political-determinants-of-oil-sector-performance.html"
        ).read_text(encoding="utf-8")
        chapter_six = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-06-west-africa-in-depth-country-analysis.html"
        ).read_text(encoding="utf-8")
        conclusion = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "general-conclusion.html"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "Principaux éléments fiscaux appliqués dans certains pays de l’Afrique de l’Ouest",
            chapter_four,
        )
        self.assertNotIn(
            "Key tax elements applied in selected West African countries",
            chapter_four,
        )
        self.assertNotIn(
            "State/Contractor income associated with the tax system in selected West African countries",
            chapter_four,
        )
        self.assertIn(
            "Le secteur pétrolier occupe une place prépondérante dans l’économie mondiale",
            chapter_five,
        )
        self.assertNotIn("The oil sector occupies a prominent place in the global economy", chapter_five)
        self.assertIn(
            "Le Nigéria est le premier producteur de pétrole d’Afrique",
            chapter_six,
        )
        self.assertNotIn("Nigeria is Africa's largest oil producer", chapter_six)
        self.assertIn(
            "L’exploration et l’exploitation des ressources pétrolières et gazières en Afrique de l’Ouest",
            conclusion,
        )
        self.assertNotIn(
            "The exploration and exploitation of oil and gas resources in West Africa",
            conclusion,
        )

    def test_french_chapter_four_table_six_keeps_the_four_column_header_grid(self) -> None:
        chapter_four = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            chapter_four,
            re.compile(
                r"<table>\s*<caption>.*?Tableau 6:.*?</caption>\s*(?:<colgroup>.*?</colgroup>\s*)?<thead>\s*"
                r"<tr>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?PAYS.*?</th>\s*"
                r"<th[^>]*colspan=\"2\"[^>]*>.*?MÉCANISMES DE PARTAGE DU PÉTROLE PROFIT.*?</th>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?PROFIT OIL DE L.?ETAT \(%\).*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?Production jounalière ou cumulée.*?</th>\s*"
                r"<th[^>]*>.*?Facteur R ou RoR.*?</th>\s*"
                r"</tr>",
                re.DOTALL,
            ),
        )

    def test_french_chapter_four_tables_five_ten_and_eleven_keep_english_header_grids(self) -> None:
        chapter_four = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html"
        ).read_text(encoding="utf-8")

        patterns = {
            5: re.compile(
                r"<table[^>]*>\s*<caption>.*?Tableau 5:.*?</caption>\s*"
                r"<colgroup>.*?</colgroup>\s*"
                r"<thead>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?</th>\s*"
                r"<th[^>]*colspan=\"4\"[^>]*>.*?ROYALTY \(%\).*?</th>\s*"
                r"<th[^>]*rowspan=\"3\"[^>]*>.*?Observations.*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?</th>\s*"
                r"<th[^>]*colspan=\"3\"[^>]*>.*?Pétrole.*?</th>\s*"
                r"<th[^>]*>.*?Gaz naturel.*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?PAYS.*?</th>\s*"
                r"<th[^>]*colspan=\"2\"[^>]*>.*?Offshore.*?</th>\s*"
                r"<th[^>]*>.*?Onshore.*?</th>\s*"
                r"<th[^>]*>.*?</th>\s*"
                r"</tr>\s*"
                r"</thead>\s*"
                r"<tbody>\s*"
                r"<tr>\s*"
                r"<td[^>]*>.*?</td>\s*"
                r"<td[^>]*>.*?Shallow.*?</td>\s*"
                r"<td[^>]*>.*?Deep.*?</td>",
                re.DOTALL,
            ),
            10: re.compile(
                r"<table[^>]*>\s*<caption>.*?Tableau 10:.*?</caption>\s*"
                r"<colgroup>.*?</colgroup>\s*"
                r"<thead>\s*"
                r"<tr>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Pays.*?</th>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Part du contractant \(%\).*?</th>\s*"
                r"<th[^>]*colspan=\"3\"[^>]*>.*?Part de l.?Etat \(%\).*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?Gouvernement.*?</th>\s*"
                r"<th[^>]*>.*?Part SNH.*?</th>\s*"
                r"<th[^>]*>.*?Total Etat.*?</th>\s*"
                r"</tr>\s*"
                r"</thead>\s*"
                r"<tbody>\s*"
                r"<tr>\s*"
                r"<td[^>]*>.*?Bénin.*?</td>",
                re.DOTALL,
            ),
            11: re.compile(
                r"<table[^>]*>\s*<caption>.*?Tableau 11:.*?</caption>\s*"
                r"<colgroup>.*?</colgroup>\s*"
                r"<thead>\s*"
                r"<tr>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Pays.*?</th>\s*"
                r"<th[^>]*colspan=\"2\"[^>]*>.*?Flux de trésorerie.*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?Contractant.*?</th>\s*"
                r"<th[^>]*>.*?Etat.*?</th>\s*"
                r"</tr>\s*"
                r"</thead>\s*"
                r"<tbody>\s*"
                r"<tr>\s*"
                r"<td[^>]*>.*?Bénin.*?</td>",
                re.DOTALL,
            ),
        }

        for table_number, pattern in patterns.items():
            with self.subTest(table=table_number):
                self.assertRegex(chapter_four, pattern)

    def test_french_chapter_four_table_six_ivory_coast_rules_keep_formula_block_layout(self) -> None:
        chapter_four = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            chapter_four,
            re.compile(
                r"<tr>\s*"
                r"<td>\s*<p><strong>COTE D.?IVOIRE</strong></p>\s*</td>\s*"
                r"<td>\s*<p>Production journalière modulée par un facteur H\)</p>\s*</td>\s*"
                r"<td>\s*<p>-</p>\s*</td>\s*"
                r"<td>\s*"
                r"<p>Négociable</p>\s*"
                r"<p><strong>32\.5% à 47,5</strong>% modulé par un facteur H pour le contractant \(Contrat Total -2019\) soit</p>\s*"
                r"<div class=\"book-formula\"[^>]*>\s*"
                r"<span class=\"book-formula-line\"[^>]*>100-\(32,5xH\) à 100-\(47,5xH\) pour l’Etat</span>\s*"
                r"</div>\s*"
                r"<div class=\"book-formula\"[^>]*>\s*"
                r"<span class=\"book-formula-line\"[^>]*>H=1,626\s*(?:&minus;|−|–|-)\s*0,141Ln \(prix du pétrole brut déflaté à décembre 2011\)</span>\s*"
                r"</div>\s*"
                r"</td>\s*"
                r"</tr>",
                re.DOTALL,
            ),
        )

    def test_french_chapter_two_table_four_keeps_the_financial_loss_subheader_inside_thead(self) -> None:
        chapter_two = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            chapter_two,
            re.compile(
                r"<table>\s*<caption>.*?Tableau 4:.*?</caption>\s*"
                r"(?:<colgroup>.*?</colgroup>\s*)?"
                r"<thead>\s*"
                r"<tr>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Pays.*?</th>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Production journalière \(bl/j\).*?</th>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Erreur de mesure/comptage \(%\).*?</th>\s*"
                r"<th[^>]*rowspan=\"2\"[^>]*>.*?Prix du baril \(\$US\).*?</th>\s*"
                r"<th[^>]*colspan=\"2\"[^>]*>.*?Perte financière \(\$US\).*?</th>\s*"
                r"</tr>\s*"
                r"<tr>\s*"
                r"<th[^>]*>.*?journalière.*?</th>\s*"
                r"<th[^>]*>.*?annuelle.*?</th>\s*"
                r"</tr>\s*"
                r"</thead>\s*"
                r"<tbody>\s*"
                r"<tr>\s*"
                r"<td[^>]*>.*?Niger.*?</td>",
                re.DOTALL,
            ),
        )

    def test_french_source_tree_no_longer_relies_on_english_placeholder_body_copy(self) -> None:
        chapter_one = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.md"
        ).read_text(encoding="utf-8")
        chapter_two = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
        ).read_text(encoding="utf-8")
        chapter_three = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-03-tax-regimes-in-the-petroleum-sector.md"
        ).read_text(encoding="utf-8")
        chapter_four = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")
        conclusion = (
            ROOT_DIR / "editions/fr/content" / "chapters" / "general-conclusion.md"
        ).read_text(encoding="utf-8")
        glossary = (ROOT_DIR / "editions/fr/content" / "chapters" / "glossary.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("The value chain of the oil industry is not structured in Africa", chapter_one)
        self.assertNotIn("The duration of an exploration license varies from 7 to 9 years", chapter_two)
        self.assertNotIn("The concession known as a license or lease is the oldest", chapter_three)
        self.assertNotIn("Table 6 below shows the mechanism used in some countries.", chapter_four)
        self.assertNotIn("All in all, after more than half a century of exploitation of oil", conclusion)
        self.assertNotIn("The concentration of hydrocarbons in a trap", glossary)

    def test_french_source_tree_uses_docx_body_without_cross_chapter_spillover_or_ocr_noise(self) -> None:
        chapter_one = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.md"
        ).read_text(encoding="utf-8")
        chapter_three = (
            ROOT_DIR
            / "editions/fr/content"
            / "chapters"
            / "chapter-03-tax-regimes-in-the-petroleum-sector.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("Le deuxième chapitre consacré à amont pétrolier", chapter_one)
        self.assertNotIn("\nChapitre 1 :\n", chapter_one)
        self.assertNotIn("VALEUR ECONOMIQUE DES RESSOURCES", chapter_three)
        self.assertFalse(chapter_three.rstrip().endswith("Chapitre 4"))

    def test_neutral_book_entry_redirects_french_browsers(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("navigator.languages", english_book_index)
        self.assertIn("/fr/book/", english_book_index)

    def test_book_home_pages_keep_cover_in_place_without_default_chapter_redirect(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        english_custom_js = next((ROOT_DIR / "public" / "book" / "theme").glob("custom-*.js"))
        french_custom_js = next((ROOT_DIR / "public" / "fr" / "book" / "theme").glob("custom-*.js"))

        for html in [english_book_index, french_book_index]:
            self.assertIn('class="book-cover-entry-link"', html)
            self.assertIn("function isBookHomePath(pathname)", html)
            self.assertIn(
                "const isCoverPage = isBookHomePath(window.location.pathname) || matchesChapterPath(coverPath);",
                html,
            )

        for script_path in [english_custom_js, french_custom_js]:
            script = script_path.read_text(encoding="utf-8")
            self.assertIn("function isBookHomePath(pathname)", script)
            self.assertIn(
                "const isCoverPage = isBookHomePath(window.location.pathname) || matchesChapterPath(coverPath);",
                script,
            )
            self.assertNotIn(
                "new URL(getDefaultChapterPath(window.location.pathname), window.location.href)",
                script,
            )
            self.assertNotIn("window.location.replace(target.href);", script)

    def test_book_root_outputs_sitemap_and_robots_reference(self) -> None:
        sitemap_path = ROOT_DIR / "public" / "book-sitemap.xml"
        robots_path = ROOT_DIR / "public" / "robots.txt"

        self.assertTrue(sitemap_path.exists())
        self.assertTrue(robots_path.exists())

        sitemap = sitemap_path.read_text(encoding="utf-8")
        robots = robots_path.read_text(encoding="utf-8")

        self.assertIn("https://upstreamatlas.com/book/", sitemap)
        self.assertIn("https://upstreamatlas.com/fr/book/", sitemap)
        self.assertIn(
            "https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html",
            sitemap,
        )
        self.assertIn(
            "https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            sitemap,
        )
        self.assertNotIn("https://upstreamatlas.com/book/chapters/cover.html", sitemap)
        self.assertNotIn("https://upstreamatlas.com/book/chapters/front-matter.html", sitemap)
        self.assertNotIn("https://upstreamatlas.com/fr/book/chapters/cover.html", sitemap)
        self.assertNotIn("https://upstreamatlas.com/fr/book/chapters/front-matter.html", sitemap)
        self.assertIn("Sitemap: https://upstreamatlas.com/book-sitemap.xml", robots)

    def test_site_robots_generation_includes_base_rules_and_book_sitemap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_public_dir = Path(temp_dir) / "public"
            temp_public_dir.mkdir(parents=True, exist_ok=True)
            robots_path = temp_public_dir / "robots.txt"

            subprocess.run(
                ["node", "scripts/generate_site_robots.mjs", str(temp_public_dir)],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            robots = robots_path.read_text(encoding="utf-8")
            self.assertIn("User-agent: *", robots)
            self.assertIn("Allow: /", robots)
            self.assertIn("Sitemap: https://upstreamatlas.com/book-sitemap.xml", robots)

    def test_canonical_book_pages_emit_non_empty_unique_metadata(self) -> None:
        for locale_root in [ROOT_DIR / "public" / "book", ROOT_DIR / "public" / "fr" / "book"]:
            seen_pairs: set[tuple[str, str]] = set()
            for page_path in self._iter_canonical_book_pages(locale_root):
                html = page_path.read_text(encoding="utf-8")
                title = self._extract_title(html)
                description = self._extract_meta_description(html)

                self.assertTrue(title, f"Expected non-empty title for {page_path}")
                self.assertTrue(description, f"Expected non-empty description for {page_path}")
                self.assertNotIn((title, description), seen_pairs, page_path)
                seen_pairs.add((title, description))

    def test_equivalent_chapter_pages_emit_reciprocal_hreflang_and_absolute_canonical_links(self) -> None:
        english_value_chain = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")
        french_value_chain = (
            ROOT_DIR
            / "public"
            / "fr"
            / "book"
            / "chapters"
            / "chapter-01-value-chain-of-the-hydrocarbon-sector.html"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html",
            self._extract_link_href(english_value_chain, "canonical"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html",
            self._extract_link_href(english_value_chain, "alternate", "en"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            self._extract_link_href(english_value_chain, "alternate", "fr"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html",
            self._extract_link_href(english_value_chain, "alternate", "x-default"),
        )

        self.assertEqual(
            "https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            self._extract_link_href(french_value_chain, "canonical"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/fr/book/chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html",
            self._extract_link_href(french_value_chain, "alternate", "fr"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/chapter-05-hydrocarbon-value-chain.html",
            self._extract_link_href(french_value_chain, "alternate", "en"),
        )

    def test_non_equivalent_english_page_keeps_self_reference_and_x_default_only(self) -> None:
        english_disclaimer = (
            ROOT_DIR / "public" / "book" / "chapters" / "disclaimer.html"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/disclaimer.html",
            self._extract_link_href(english_disclaimer, "canonical"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/disclaimer.html",
            self._extract_link_href(english_disclaimer, "alternate", "en"),
        )
        self.assertEqual(
            "https://upstreamatlas.com/book/chapters/disclaimer.html",
            self._extract_link_href(english_disclaimer, "alternate", "x-default"),
        )
        self.assertIsNone(self._extract_link_href(english_disclaimer, "alternate", "fr"))

    def test_book_pages_emit_page_type_specific_structured_data(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        english_value_chain = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")
        french_general_introduction = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "general-introduction.html"
        ).read_text(encoding="utf-8")
        french_glossary = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "glossary.html"
        ).read_text(encoding="utf-8")

        english_index_blocks = self._extract_json_ld_blocks(english_book_index)
        french_index_blocks = self._extract_json_ld_blocks(french_book_index)
        english_chapter_blocks = self._extract_json_ld_blocks(english_value_chain)
        french_chapter_blocks = self._extract_json_ld_blocks(french_general_introduction)
        french_glossary_blocks = self._extract_json_ld_blocks(french_glossary)

        self.assertTrue(
            any(block.get("@type") == "Book" for block in english_index_blocks if isinstance(block, dict))
        )
        self.assertTrue(
            any(block.get("@type") == "Book" for block in french_index_blocks if isinstance(block, dict))
        )
        self.assertTrue(
            any(block.get("@type") == "Chapter" for block in english_chapter_blocks if isinstance(block, dict))
        )
        self.assertTrue(
            any(block.get("@type") == "Chapter" for block in french_chapter_blocks if isinstance(block, dict))
        )
        self.assertTrue(
            any(
                block.get("@type") == "BreadcrumbList"
                for block in english_chapter_blocks
                if isinstance(block, dict)
            )
        )
        self.assertTrue(
            any(
                block.get("@type") == "BreadcrumbList"
                for block in french_chapter_blocks
                if isinstance(block, dict)
            )
        )
        self.assertTrue(
            any(block.get("@type") == "WebPage" for block in french_glossary_blocks if isinstance(block, dict))
        )
        self.assertTrue(
            any(
                block.get("@type") == "BreadcrumbList"
                for block in french_glossary_blocks
                if isinstance(block, dict)
            )
        )

    def test_book_landing_structured_data_declares_single_locale_language(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )

        english_book_schema = next(
            block
            for block in self._extract_json_ld_blocks(english_book_index)
            if isinstance(block, dict) and block.get("@type") == "Book"
        )
        french_book_schema = next(
            block
            for block in self._extract_json_ld_blocks(french_book_index)
            if isinstance(block, dict) and block.get("@type") == "Book"
        )

        self.assertEqual("en", english_book_schema.get("inLanguage"))
        self.assertEqual("fr", french_book_schema.get("inLanguage"))

    def test_redirect_only_cover_and_front_matter_point_to_book_root(self) -> None:
        english_cover = (
            ROOT_DIR / "public" / "book" / "chapters" / "cover.html"
        ).read_text(encoding="utf-8")
        french_cover = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "cover.html"
        ).read_text(encoding="utf-8")
        english_front_matter = (
            ROOT_DIR / "public" / "book" / "chapters" / "front-matter.html"
        ).read_text(encoding="utf-8")
        french_front_matter = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "front-matter.html"
        ).read_text(encoding="utf-8")

        for html, canonical in [
            (english_cover, "https://upstreamatlas.com/book/"),
            (french_cover, "https://upstreamatlas.com/fr/book/"),
            (english_front_matter, "https://upstreamatlas.com/book/"),
            (french_front_matter, "https://upstreamatlas.com/fr/book/"),
        ]:
            self.assertEqual(canonical, self._extract_link_href(html, "canonical"))
            self.assertEqual("noindex,follow", self._extract_meta_content(html, "robots"))
            self.assertEqual([], self._extract_json_ld_blocks(html))
            self.assertIn('http-equiv="refresh" content="0; url=../"', html)
            self.assertIn('window.location.replace(target)', html)
            self.assertIn('href="../"', html)
            self.assertNotIn('rel="alternate" hreflang=', html)

        self.assertIn("Cette page a été déplacée", french_cover)
        self.assertIn("Cette page a été déplacée", french_front_matter)

    def test_book_navigation_links_use_book_root_instead_of_cover_alias(self) -> None:
        english_book_index = (ROOT_DIR / "public" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        french_list_of_figures = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "list-of-figures.html"
        ).read_text(encoding="utf-8")

        self.assertIn('href="./"', english_book_index)
        self.assertNotIn('href="index.html"', english_book_index)
        self.assertNotIn('href="chapters/cover.html"', english_book_index)
        self.assertIn('href="../"', french_list_of_figures)
        self.assertNotIn('href="../index.html"', french_list_of_figures)
        self.assertNotIn('href="cover.html"', french_list_of_figures)

    def test_raw_toc_resources_use_book_root_instead_of_cover_alias(self) -> None:
        for locale_root in [ROOT_DIR / "public" / "book", ROOT_DIR / "public" / "fr" / "book"]:
            toc_html = (locale_root / "toc.html").read_text(encoding="utf-8")
            self.assertNotIn('href="chapters/cover.html"', toc_html)

            for toc_script in locale_root.glob("toc-*.js"):
                toc_script_text = toc_script.read_text(encoding="utf-8")
                self.assertNotIn('href="chapters/cover.html"', toc_script_text)

    def test_seo_reinjection_preserves_non_managed_json_ld_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_book_dir = Path(temp_dir) / "book"
            shutil.copytree(ROOT_DIR / "public" / "book", temp_book_dir)
            target_page = temp_book_dir / "index.html"
            preserved_block = (
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@type":"Thing","name":"Preserved fixture"}'
                "</script>"
            )
            html = target_page.read_text(encoding="utf-8").replace(
                "</head>",
                f"        {preserved_block}\n    </head>",
            )
            target_page.write_text(html, encoding="utf-8")

            subprocess.run(
                ["node", "scripts/inject_book_seo.mjs", str(temp_book_dir), "en"],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            reinjected_html = target_page.read_text(encoding="utf-8")
            json_ld_types = [
                block.get("@type")
                for block in self._extract_json_ld_blocks(reinjected_html)
                if isinstance(block, dict)
            ]

            self.assertIn("Preserved fixture", reinjected_html)
            self.assertIn("Thing", json_ld_types)
            self.assertIn("Book", json_ld_types)

    def test_seo_reinjection_replaces_stale_canonical_and_hreflang_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_book_dir = Path(temp_dir) / "book"
            shutil.copytree(ROOT_DIR / "public" / "book", temp_book_dir)
            target_page = temp_book_dir / "chapters" / "chapter-05-hydrocarbon-value-chain.html"
            stale_head_markup = (
                '<link rel="canonical" href="https://stale.example.com/book/old.html">\n'
                '        <link rel="alternate" hreflang="en" href="https://stale.example.com/book/old.html">\n'
                '        <link rel="alternate" hreflang="fr" href="https://stale.example.com/fr/book/old.html">\n'
            )
            html = target_page.read_text(encoding="utf-8").replace(
                "</head>",
                f"        {stale_head_markup}</head>",
            )
            target_page.write_text(html, encoding="utf-8")

            subprocess.run(
                ["node", "scripts/inject_book_seo.mjs", str(temp_book_dir), "en"],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            reinjected_html = target_page.read_text(encoding="utf-8")
            self.assertEqual(1, len(re.findall(r'<link rel="canonical" ', reinjected_html)))
            self.assertEqual(3, len(re.findall(r'<link rel="alternate" ', reinjected_html)))
            self.assertNotIn("stale.example.com", reinjected_html)

    def test_seo_injection_preserves_static_chapter_body_text(self) -> None:
        english_value_chain = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-05-hydrocarbon-value-chain.html"
        ).read_text(encoding="utf-8")

        self.assertIn("Chapter 5: Hydrocarbon Value Chain", english_value_chain)
        self.assertIn(
            "The upstream petroleum sector forms the foundation of the petroleum industry",
            english_value_chain,
        )


if __name__ == "__main__":
    unittest.main()
