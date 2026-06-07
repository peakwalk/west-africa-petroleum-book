from __future__ import annotations

import unittest
from pathlib import Path

from scripts.docx_figures.chart_svg import parse_chart_part, render_chart_svg

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCX_PATH = ROOT_DIR / "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"


class ChartSvgTest(unittest.TestCase):
    def test_parse_chart24_preserves_sparse_series_points(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart2.xml")

        self.assertEqual(chart.chart_type, "barChart")
        self.assertEqual(
            chart.categories,
            ["Ghana", "Benin", "Ivory Coast", "Senegal", "Nigeria", "Niger"],
        )
        self.assertEqual([series.title for series in chart.series], [
            "Cost stop",
            "1000-3000 m min S/DW Min ONS",
            "> 3000 m DW UDW Max",
        ])
        self.assertEqual(chart.series[0].values, [0.0, 70.0, 60.0, 55.0, 60.0, None])
        self.assertEqual(chart.series[1].values, [None, 75.0, None, 60.0, None, 70.0])
        self.assertEqual(chart.series[2].values, [None, 80.0, 80.0, 70.0, 70.0, None])
        self.assertEqual(chart.value_axis_title, "Cost stop/Depreciation")

    def test_parse_chart31_series_values(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart3.xml")

        self.assertEqual(chart.chart_type, "bar3DChart")
        self.assertEqual(chart.value_axis_title, "Share (%)")
        self.assertEqual([series.title for series in chart.series], ["Contractor", "State"])
        self.assertEqual(chart.series[0].values, [34.1, 41.23, 41.4, 13.5, 32.47, 34.0])
        self.assertEqual(chart.series[1].values, [65.9, 58.77, 58.6, 86.5, 67.53, 66.0])

    def test_parse_chart19_line_series_values(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart1.xml")

        self.assertEqual(chart.chart_type, "lineChart")
        self.assertEqual(chart.value_axis_title, "Annual production (mbbls/year)")
        self.assertEqual(chart.categories[:5], ["0", "2", "4", "6", "8"])
        self.assertEqual(chart.series[0].values[:6], [0.0, 0.0, 0.0, 0.0, 550.0, 1095.0])
        self.assertEqual(chart.series[1].values[:6], [0.0, 0.0, 0.0, 0.0, 250.0, 500.0])

    def test_render_chart_svg_contains_labels_and_legend(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart4.xml")

        svg = render_chart_svg(chart, width=1200, height=760)

        self.assertIn("<svg", svg)
        self.assertIn("Contractor", svg)
        self.assertIn("State", svg)
        self.assertIn("Benin", svg)
        self.assertIn("75.62", svg)

    def test_render_line_chart_svg_contains_axis_labels(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart1.xml")

        svg = render_chart_svg(chart, width=1200, height=760)

        self.assertIn("<svg", svg)
        self.assertIn("Annual production (mbbls/year)", svg)
        self.assertIn("polyline", svg)
        self.assertIn(">46<", svg)

    def test_render_chart24_svg_uses_english_axis_and_category_labels(self) -> None:
        chart = parse_chart_part(DOCX_PATH, "word/charts/chart2.xml")

        svg = render_chart_svg(chart, width=1200, height=760)

        self.assertIn("&gt; 3000 m DW UDW Max", svg)
        self.assertIn("Benin", svg)
        self.assertIn("Ivory Coast", svg)
        self.assertNotIn("PAYS", svg)
        self.assertNotIn("Pays", svg)


if __name__ == "__main__":
    unittest.main()
