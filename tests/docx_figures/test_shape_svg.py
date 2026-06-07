from __future__ import annotations

import unittest
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from scripts.docx_figures.inventory import build_figure_inventory
from scripts.docx_figures.shape_svg import render_shape_figure_svg

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCX_PATH = ROOT_DIR / "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
SUMMARY_PATH = ROOT_DIR / "src/SUMMARY.md"
CHAPTERS_DIR = ROOT_DIR / "src/chapters"


class ShapeSvgTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = {
            record.number: record
            for record in build_figure_inventory(DOCX_PATH, CHAPTERS_DIR, SUMMARY_PATH)
        }

    def test_render_shape_figure_23_contains_taxonomy_labels(self) -> None:
        record = self.inventory[23]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("<svg", svg)
        self.assertIn("PETROLEUM TAX REGIMES", svg)
        self.assertIn("CONTRACTUAL SYSTEMS", svg)
        self.assertIn("Production Sharing Contracts", svg)

    def test_render_shape_figure_25_contains_flowchart_labels(self) -> None:
        record = self.inventory[25]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("<svg", svg)
        self.assertIn("REGIME FISCAL", svg)
        self.assertIn("Gross income: 100", svg)
        self.assertIn("Gross cash flow", svg)
        self.assertIn("FLOW CHART BENIN", svg)

    def test_render_shape_figure_17_from_standalone_vml_shapes(self) -> None:
        record = self.inventory[17]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("<svg", svg)
        self.assertIn("RAW DATA COLLECTION", svg)
        self.assertIn("PROCESSING AND INTERPRETATION OF THE DATA COLLECTED", svg)
        self.assertIn("ECONOMIC EVALUATION AND DECISIONS", svg)

    def test_render_shape_figure_26_uses_foreign_object_text_layout(self) -> None:
        record = self.inventory[26]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("<foreignObject", svg)
        self.assertIn("display:flex", svg)
        self.assertIn("Profit sharing Oil, 20%&lt;ROR&lt;25%, 15% tax", svg)

    def test_render_shape_figure_26_uses_docx_theme_font_family(self) -> None:
        record = self.inventory[26]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("font-family:Calibri", svg)

    def test_render_shape_figure_26_includes_translucent_star_path(self) -> None:
        record = self.inventory[26]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        self.assertTrue(root.findall("svg:path", namespace))
        self.assertTrue(root.findall("svg:defs/svg:radialGradient", namespace))

    def test_render_shape_figure_26_places_star_inside_main_viewbox(self) -> None:
        record = self.inventory[26]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        path = root.find("svg:path", namespace)
        self.assertIsNotNone(path)
        numbers = [
            float(value)
            for value in __import__("re").findall(r"-?\d+(?:\.\d+)?", path.attrib["d"])
        ]
        xs = numbers[0::2]
        ys = numbers[1::2]
        self.assertGreater(min(xs), 10000.0)
        self.assertGreater(min(ys), 25000.0)

    def test_render_shape_figure_26_includes_corporate_tax_overlay_row(self) -> None:
        record = self.inventory[26]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("Corporate tax:", svg)
        self.assertIn("52,88", svg)

    def test_render_shape_figure_30_includes_center_circle_geometry(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        paths = root.findall("svg:path", namespace)
        self.assertTrue(paths or root.findall("svg:ellipse", namespace))
        if paths:
            self.assertGreaterEqual(len(re.findall(r"-?\d+(?:\.\d+)?", paths[0].attrib["d"])), 40)
        self.assertIn("#ffc000", svg.lower())

    def test_render_shape_figure_30_preserves_all_overlay_rows(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertIn("Net cash flow", svg)
        self.assertIn("State participation: 10%", svg)
        self.assertIn("Total gross cash flow of the contractor", svg)
        self.assertIn("73,27", svg)
        self.assertIn("+1,53", svg)
        self.assertIn("-1,53", svg)

    def test_render_shape_figure_30_keeps_circle_above_net_cash_flow(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        path = root.find("svg:path", namespace)
        self.assertIsNotNone(path)
        numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", path.attrib["d"])]
        ys = numbers[1::2]
        self.assertLess(max(ys), 47000.0)
        self.assertLess(float(path.attrib.get("fill-opacity", "1.0")), 0.6)

    def test_render_shape_figure_30_renders_circle_below_text_layers(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        self.assertLess(svg.index("<path "), svg.index("REGIME FISCAL"))
        self.assertLess(svg.index("<path "), svg.index("Profit sharing Oil"))

    def test_render_shape_figure_30_keeps_regime_title_padding_small(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        regime_style = None
        for foreign_object in root.findall("{http://www.w3.org/2000/svg}foreignObject"):
            text = " ".join(
                " ".join((node.text or "").split())
                for node in foreign_object.iter()
                if (node.text or "").strip()
            )
            if text == "REGIME FISCAL":
                regime_style = list(foreign_object)[0].attrib.get("style", "")
                break

        self.assertIsNotNone(regime_style)
        match = re.search(r"padding:([0-9.]+)px", regime_style)
        self.assertIsNotNone(match)
        self.assertLess(float(match.group(1)), 600.0)

    def test_render_shape_figure_30_keeps_gap_between_profit_sharing_and_imposable(self) -> None:
        record = self.inventory[30]

        svg = render_shape_figure_svg(
            DOCX_PATH,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )

        root = ET.fromstring(svg)
        positions: dict[str, tuple[float, float]] = {}
        for foreign_object in root.findall("{http://www.w3.org/2000/svg}foreignObject"):
            text = " ".join(
                " ".join((node.text or "").split())
                for node in foreign_object.iter()
                if (node.text or "").strip()
            )
            if text in {"Profit sharing Oil 60/40", "Imposable/taxable :0"}:
                positions[text] = (
                    float(foreign_object.attrib["y"]),
                    float(foreign_object.attrib["height"]),
                )

        self.assertIn("Profit sharing Oil 60/40", positions)
        self.assertIn("Imposable/taxable :0", positions)
        profit_y, profit_height = positions["Profit sharing Oil 60/40"]
        imposable_y, _ = positions["Imposable/taxable :0"]
        self.assertGreaterEqual(imposable_y - (profit_y + profit_height), 800.0)


if __name__ == "__main__":
    unittest.main()
