from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.check_docx_parity import chapter_anchor
from scripts.docx_parity.extract_docx import extract_docx_chapter_by_anchors
from scripts.docx_parity.extract_markdown import _parse_chapter
from scripts.docx_parity.model import ChapterSemanticModel


ROOT_DIR = Path(__file__).resolve().parents[1]
FR_DOCX = ROOT_DIR / "resources" / "editions" / "fr" / "reference.docx"
FR_SUMMARY = ROOT_DIR / "src-fr" / "SUMMARY.md"
SRC_FR_DIR = ROOT_DIR / "src-fr" / "chapters"

FR_CHAPTER_FILES = {
    "CHAINE DES VALEURS DU SECTEUR DES HYDROCARBURES": "chapter-01-value-chain-of-the-hydrocarbon-sector.md",
    "DIFFERENTES PHASES DE L’AMONT PETROLIER ET ROLES DES ETATS": "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md",
    "REGIMES FISCAUX DANS LE SECTEUR PETROLIER": "chapter-03-tax-regimes-in-the-petroleum-sector.md",
    "ETUDE COMPAREE DES REGIMES FISCAUX DANS CERTAINS PAYS DE L’AFRIQUE DE L’OUEST :": "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md",
    "PRINCIPAUX DETERMINANTS SOCIO-POLITIQUES DE LA PERFORMANCE DU SECTEUR PETROLIER": "chapter-05-key-socio-political-determinants-of-oil-sector-performance.md",
    "AFRIQUE DE L'OUEST : ANALYSES APPROFONDIES PAR PAYS": "chapter-06-west-africa-in-depth-country-analysis.md",
}


class FrenchSemanticRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chapter_specs = list(FR_CHAPTER_FILES.items())

    def _anchored_docx_chapter(self, index: int) -> ChapterSemanticModel:
        _, file_name = self.chapter_specs[index]
        chapter_path = SRC_FR_DIR / file_name
        markdown_chapter = _parse_chapter(chapter_path)

        next_anchor = None
        if index + 1 < len(self.chapter_specs):
            _, next_file_name = self.chapter_specs[index + 1]
            next_anchor = chapter_anchor(_parse_chapter(SRC_FR_DIR / next_file_name))

        return extract_docx_chapter_by_anchors(
            FR_DOCX,
            chapter_title=markdown_chapter.title,
            start_anchor=chapter_anchor(markdown_chapter),
            end_anchor=next_anchor,
        ).chapters[0]

    def test_french_body_chapters_match_the_reference_docx_anchor_parity_model(self) -> None:
        for index, (title, file_name) in enumerate(self.chapter_specs):
            with self.subTest(chapter=title):
                markdown_chapter = _parse_chapter(SRC_FR_DIR / file_name)
                docx_chapter = self._anchored_docx_chapter(index)

                self.assertEqual(docx_chapter.outline, markdown_chapter.outline)
                self.assertEqual(docx_chapter.body, markdown_chapter.body)

    def test_chapter_four_table_blocks_are_semantic_html(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")

        for table_number in (5, 6, 7):
            with self.subTest(table=table_number):
                match = re.search(
                    rf"<table\b.*?<caption><p>Tableau {table_number}:.*?</table>",
                    chapter_four,
                    re.DOTALL,
                )
                self.assertIsNotNone(match)
                assert match is not None
                table_html = match.group(0)

                self.assertNotIn('cellspacing="0"', table_html)
                self.assertNotIn('cellpadding="0"', table_html)
                self.assertNotIn('class="t1"', table_html)
                self.assertIn("<thead>", table_html)
                self.assertIn("<tbody>", table_html)
                self.assertIn("<th", table_html)

    def test_chapter_four_table_six_keeps_country_rows_in_tbody(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")
        match = re.search(
            r"<table>\s*<caption><p>Tableau 6:.*?</thead>\s*<tbody>(?P<tbody>.*?)</tbody>\s*</table>",
            chapter_four,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        assert match is not None
        thead_html = match.group(0).split("</thead>", 1)[0]
        tbody_html = match.group("tbody")

        self.assertNotIn("BÉNIN", thead_html)
        self.assertIn("BÉNIN", tbody_html)

    def test_chapter_four_table_six_matches_english_multi_row_header_structure(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            chapter_four,
            re.compile(
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

    def test_chapter_four_tables_five_ten_and_eleven_match_english_header_grids(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")

        patterns = {
            5: re.compile(
                r"<table[^>]*>\s*<caption><p>Tableau 5:.*?</p></caption>\s*"
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
                r"<table[^>]*>\s*<caption><p>Tableau 10:.*?</p></caption>\s*"
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
                r"<table[^>]*>\s*<caption><p>Tableau 11:.*?</p></caption>\s*"
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

    def test_chapter_four_table_six_ivory_coast_rules_use_semantic_formula_blocks(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
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

    def test_chapter_two_table_four_matches_english_multi_row_header_structure(self) -> None:
        chapter_two = (
            SRC_FR_DIR / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            chapter_two,
            re.compile(
                r"<table>\s*<caption><p>Tableau 4:.*?</p></caption>\s*"
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

    def test_chapter_two_formula_blocks_are_semantic_html(self) -> None:
        chapter_two = (
            SRC_FR_DIR / "chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            'class="formula-group formula-group--prospect" data-equation-label="2.1"',
            chapter_two,
        )
        self.assertIn(
            'P(prospect) = P(roche mère) x P(réservoir) x P(piège)',
            chapter_two,
        )
        self.assertIn("Piège étanche + couverture imperméable", chapter_two)
        self.assertIn(
            'class="formula-group formula-group--volumetric" data-equation-label="2.2"',
            chapter_two,
        )
        self.assertIn('class="formula-case-title">Pour l’huile</p>', chapter_two)
        self.assertIn('class="formula-case-title">Pour le gaz</p>', chapter_two)

    def test_chapter_four_formula_blocks_are_semantic_html(self) -> None:
        chapter_four = (
            SRC_FR_DIR / "chapter-04-comparative-study-of-tax-regimes-in-selected-west-african-countries.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            '<div class="book-formula" data-equation-label="4.1"',
            chapter_four,
        )
        self.assertIn(
            'Revenu Post Royalty = Revenu brut &minus; Royalty',
            chapter_four,
        )
        self.assertIn(
            'class="formula-group formula-group--split formula-group--oil-profit" data-equation-label="4.2"',
            chapter_four,
        )
        self.assertIn("Pétrole profit = Revenue post Royalty", chapter_four)
        self.assertIn(
            'class="formula-panel formula-panel--r-factor" data-equation-label="4.3"',
            chapter_four,
        )
        self.assertIn('data-formula-label="d)"', chapter_four)

    def test_glossary_api_density_formula_is_semantic_html(self) -> None:
        glossary = (SRC_FR_DIR / "glossary.md").read_text(encoding="utf-8")

        self.assertIn('class="book-formula api-density-formula"', glossary)
        self.assertIn("Densité&nbsp;API&nbsp;=", glossary)
        self.assertIn("Densité&nbsp;à&nbsp;15&deg;C", glossary)


if __name__ == "__main__":
    unittest.main()
