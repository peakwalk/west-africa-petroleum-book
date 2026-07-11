from __future__ import annotations

from html.parser import HTMLParser
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


class CountryCardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cards: list[dict[str, object]] = []
        self.current_card: dict[str, object] | None = None
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
        elif tag == "a" and "country-analysis-link" in classes:
            self.current_card["has_analysis_link"] = True

    def handle_endtag(self, tag: str) -> None:
        if self.current_card is None:
            return

        if tag == "dd" and self.current_metric_text is not None:
            labels = self.current_card["metric_labels"]
            assert isinstance(labels, list)
            labels.append("".join(self.current_metric_text).strip())
            self.current_metric_text = None
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

        self.assertEqual(len(parser.cards), 16)
        self.assertIn("1000+ Discoveries", homepage_html)
        for card in parser.cards:
            self.assertEqual(card["metric_rows"], 1)
            self.assertEqual(card["metric_labels"], ["Producing Fields"])
            self.assertTrue(card["has_analysis_link"])
            card_text = "".join(card["text"])
            self.assertNotIn("Discoveries", card_text)
            self.assertNotIn("Decouvertes", card_text)
