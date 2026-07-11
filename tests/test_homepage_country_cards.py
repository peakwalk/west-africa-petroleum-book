from __future__ import annotations

from html.parser import HTMLParser
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
COUNTRY_ANALYSIS_LINKS = {
    "Nigeria": (
        "Chapter 3.1 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#31--nigeria",
    ),
    "Ghana": (
        "Chapter 3.2 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#32--ghana",
    ),
    "Côte d'Ivoire": (
        "Chapter 3.3 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#33--côte-divoire",
    ),
    "Senegal": (
        "Chapter 3.4 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#34--senegal",
    ),
    "Mauritania": (
        "Chapter 3.5 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#35--mauritania",
    ),
    "Niger": (
        "Chapter 3.6 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#36--niger",
    ),
    "Benin": (
        "Chapter 3.7 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#37--benin",
    ),
    "Liberia": (
        "Chapter 3.8 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#38--liberia",
    ),
    "Sierra Leone": (
        "Chapter 3.9 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#39--sierra-leone",
    ),
    "Guinea": (
        "Chapter 3.10 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#310--guinea",
    ),
    "Guinea-Bissau": (
        "Chapter 3.11 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#311--guinea-bissau",
    ),
    "The Gambia": (
        "Chapter 3.12 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#312--the-gambia",
    ),
    "Togo": (
        "Chapter 3.13 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#313--togo",
    ),
    "Burkina Faso": (
        "Chapter 3.14 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#314--burkina-faso",
    ),
    "Mali": (
        "Chapter 3.15 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#315--mali",
    ),
    "Cabo Verde": (
        "Chapter 3.16 →",
        "/book/chapters/chapter-03-west-africa-country-analysis.html#316--cabo-verde",
    ),
}


class CountryCardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict[str, object]] = []
        self.current_card: dict[str, object] | None = None
        self.current_analysis_link_text: list[str] | None = None
        self.current_country_name_text: list[str] | None = None
        self.in_metrics = False
        self.current_metric_text: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set((dict(attrs).get("class") or "").split())

        if tag == "article" and "country-card-v2" in classes:
            self.current_card = {
                "has_analysis_link": False,
                "metric_labels": [],
                "metric_rows": 0,
                "text": [],
            }
            return

        if self.current_card is None:
            return

        if tag == "dl" and "country-metrics" in classes:
            self.in_metrics = True
        elif tag == "div" and self.in_metrics:
            self.current_card["metric_rows"] = int(self.current_card["metric_rows"]) + 1
        elif tag == "dd" and self.in_metrics:
            self.current_metric_text = []
        elif tag == "span" and "country-name" in classes:
            self.current_country_name_text = []
        elif tag == "a" and "country-analysis-link" in classes:
            self.current_card["has_analysis_link"] = True
            self.current_card["analysis_href"] = dict(attrs).get("href")
            self.current_analysis_link_text = []

    def handle_endtag(self, tag: str) -> None:
        if self.current_card is None:
            return

        if tag == "dd" and self.current_metric_text is not None:
            labels = self.current_card["metric_labels"]
            assert isinstance(labels, list)
            labels.append("".join(self.current_metric_text).strip())
            self.current_metric_text = None
        elif tag == "span" and self.current_country_name_text is not None:
            self.current_card["country_name"] = "".join(self.current_country_name_text).strip()
            self.current_country_name_text = None
        elif tag == "a" and self.current_analysis_link_text is not None:
            self.current_card["analysis_label"] = "".join(
                self.current_analysis_link_text
            ).strip()
            self.current_analysis_link_text = None
        elif tag == "dl" and self.in_metrics:
            self.in_metrics = False
        elif tag == "article":
            self.cards.append(self.current_card)
            self.current_card = None

    def handle_data(self, data: str) -> None:
        if self.current_card is None:
            return

        text = self.current_card["text"]
        assert isinstance(text, list)
        text.append(data)
        if self.current_metric_text is not None:
            self.current_metric_text.append(data)
        if self.current_country_name_text is not None:
            self.current_country_name_text.append(data)
        if self.current_analysis_link_text is not None:
            self.current_analysis_link_text.append(data)


class HomepageCountryCardTests(unittest.TestCase):
    def test_generated_country_cards_render_only_producing_field_metrics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="homepage-country-cards-") as temp_dir:
            output_root = Path(temp_dir)
            subprocess.run(
                ["node", "scripts/generate-index-page.mjs", "--output-root", str(output_root)],
                cwd=ROOT_DIR,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            homepage_html = (output_root / "index.html").read_text(encoding="utf-8")

        parser = CountryCardParser()
        parser.feed(homepage_html)

        self.assertEqual(len(parser.cards), len(COUNTRY_ANALYSIS_LINKS))
        self.assertIn("1000+ Discoveries", homepage_html)
        cards_by_country = {
            card["country_name"]: card
            for card in parser.cards
            if "country_name" in card
        }
        self.assertEqual(set(cards_by_country), set(COUNTRY_ANALYSIS_LINKS))

        for card in parser.cards:
            self.assertEqual(card["metric_rows"], 1)
            self.assertEqual(card["metric_labels"], ["Producing Fields"])
            self.assertTrue(card["has_analysis_link"])
            card_text = "".join(card["text"])
            self.assertNotIn("Discoveries", card_text)
            self.assertNotIn("Decouvertes", card_text)

        for country, (label, href) in COUNTRY_ANALYSIS_LINKS.items():
            card = cards_by_country[country]
            self.assertEqual(card["analysis_label"], label)
            self.assertEqual(card["analysis_href"], href)
            self.assertNotEqual(card["analysis_label"], "Country Analysis →")
