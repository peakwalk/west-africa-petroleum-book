from __future__ import annotations

import unittest

from scripts.sync_fr_semantic_blocks import _collect_block_spans


class SyncFrSemanticBlocksTests(unittest.TestCase):
    def test_collect_block_spans_ignores_multiline_html_table_contents(self) -> None:
        lines = [
            "# Chapitre 4",
            "",
            "## 4.2- Key tax elements applied in selected West African countries",
            "",
            "Le tableau ci-dessous présente les mécanismes.",
            "",
            "<table>",
            "<caption><p>Table 6:</p></caption>",
            "<tr>",
            "<th>COUNTRY</th>",
            "Narrative text that should stay inside the table block",
            "</tr>",
            "</table>",
            "",
            "Paragraph after the table.",
        ]

        title_index, heading_spans, body_spans = _collect_block_spans(lines)

        self.assertEqual(title_index, 0)
        self.assertEqual([(span.start, span.end) for span in heading_spans], [(2, 2)])
        self.assertEqual(
            [(span.kind, span.start, span.end) for span in body_spans],
            [("paragraph", 4, 4), ("html_table", 6, 12), ("paragraph", 14, 14)],
        )


if __name__ == "__main__":
    unittest.main()
