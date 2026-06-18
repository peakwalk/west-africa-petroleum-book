from __future__ import annotations

import re
import shutil
import subprocess
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

    def test_dual_book_outputs_are_published(self) -> None:
        self.assertTrue((ROOT_DIR / "public" / "book" / "index.html").exists())
        self.assertTrue((ROOT_DIR / "public" / "fr" / "book" / "index.html").exists())

    def test_book_header_exposes_cross_edition_switch(self) -> None:
        english_chapter = (ROOT_DIR / "public" / "book" / "chapters" / "foreword.html").read_text(
            encoding="utf-8"
        )
        french_chapter = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")

        self.assertIn('class="reader-language-switch"', english_chapter)
        self.assertIn('/fr/book/chapters/foreword.html?lang=fr', english_chapter)
        self.assertIn('class="reader-language-switch"', french_chapter)
        self.assertIn('/book/chapters/foreword.html?lang=en', french_chapter)

    def test_book_header_language_switch_keeps_en_then_fr_order_without_label(self) -> None:
        english_chapter = (ROOT_DIR / "public" / "book" / "chapters" / "foreword.html").read_text(
            encoding="utf-8"
        )
        french_chapter = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")

        self.assertNotIn('class="reader-language-label"', english_chapter)
        self.assertNotIn('class="reader-language-label"', french_chapter)

        self.assertRegex(
            english_chapter,
            re.compile(
                r'<nav class="reader-language-switch"[^>]*>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">EN</span>\s*'
                r'<a class="reader-language-option" href="/fr/book/chapters/foreword\.html\?lang=fr" lang="fr" hreflang="fr">FR</a>\s*'
                r'</nav>'
            ),
        )
        self.assertRegex(
            french_chapter,
            re.compile(
                r'<nav class="reader-language-switch"[^>]*>\s*'
                r'<a class="reader-language-option" href="/book/chapters/foreword\.html\?lang=en" lang="en" hreflang="en">EN</a>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">FR</span>\s*'
                r'</nav>'
            ),
        )

    def test_book_reader_injects_toolbar_and_sidebar_language_switches(self) -> None:
        english_chapter = (ROOT_DIR / "public" / "book" / "chapters" / "foreword.html").read_text(
            encoding="utf-8"
        )
        french_chapter = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "foreword.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            english_chapter,
            re.compile(
                r'<div class="book-sidebar-intro">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="sidebar"[^>]*>\s*'
                r'<span class="reader-language-option is-current" aria-current="page">EN</span>\s*'
                r'<a class="reader-language-option" href="/fr/book/chapters/foreword\.html\?lang=fr" lang="fr" hreflang="fr">FR</a>\s*'
                r'</nav>\s*'
                r'<p class="book-sidebar-book-title">',
                re.DOTALL,
            ),
        )
        self.assertRegex(
            english_chapter,
            re.compile(
                r'<div class="toolbar-actions">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="toolbar"[^>]*>',
                re.DOTALL,
            ),
        )
        self.assertRegex(
            french_chapter,
            re.compile(
                r'<div class="book-sidebar-intro">\s*'
                r'<nav class="reader-language-switch"[^>]*data-reader-language-switch="sidebar"[^>]*>\s*'
                r'<a class="reader-language-option" href="/book/chapters/foreword\.html\?lang=en" lang="en" hreflang="en">EN</a>\s*'
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
        english_cover = (
            ROOT_DIR / "public" / "book" / "chapters" / "cover.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="images/figure-000.webp"', english_book_index)
        self.assertNotIn('src="images/figure-001.webp"', english_book_index)
        self.assertIn('src="../images/figure-000.webp"', english_cover)
        self.assertNotIn('src="../images/figure-001.webp"', english_cover)

    def test_french_book_cover_uses_french_cover_asset(self) -> None:
        french_book_index = (ROOT_DIR / "public" / "fr" / "book" / "index.html").read_text(
            encoding="utf-8"
        )
        french_cover = (
            ROOT_DIR / "public" / "fr" / "book" / "chapters" / "cover.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="images/figure-000.webp"', french_book_index)
        self.assertNotIn('src="images/figure-001.webp"', french_book_index)
        self.assertIn('src="../images/figure-000.webp"', french_cover)
        self.assertNotIn('src="../images/figure-001.webp"', french_cover)

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

    def test_english_chapter_two_figure_nine_uses_full_webp_asset(self) -> None:
        english_chapter_two = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-009.webp"', english_chapter_two)
        self.assertNotIn('src="../images/figure-009.png"', english_chapter_two)
        self.assertNotIn('src="../images/figure-009.jpg"', english_chapter_two)

    def test_english_chapter_two_figure_ten_uses_full_webp_asset(self) -> None:
        english_chapter_two = (
            ROOT_DIR
            / "public"
            / "book"
            / "chapters"
            / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html"
        ).read_text(encoding="utf-8")

        self.assertIn('src="../images/figure-010.webp"', english_chapter_two)
        self.assertNotIn('src="../images/figure-010.png"', english_chapter_two)

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


if __name__ == "__main__":
    unittest.main()
