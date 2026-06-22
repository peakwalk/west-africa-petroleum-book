import unittest

from scripts.docx_parity.model import BodyBlock, ChapterSemanticModel, OutlineEntry
from scripts.docx_parity.render_markdown import render_markdown_chapter


class RenderMarkdownChapterTests(unittest.TestCase):
    def test_renders_outline_entries_at_recorded_body_boundaries(self) -> None:
        chapter = ChapterSemanticModel(
            source_path="editions/en/content/chapters/chapter-01-general-introduction.md",
            title="Chapter 1: General Introduction",
            outline=[
                OutlineEntry(level=2, number="1.1-", title="Hydrocarbon Resources"),
                OutlineEntry(level=3, number="1.1.1-", title="Contribution to Growth"),
                OutlineEntry(level=2, number="1.2-", title="Future Potential"),
            ],
            body=[
                BodyBlock(kind="paragraph", text="West Africa has significant resources."),
                BodyBlock(
                    kind="caption",
                    text="Figure 1: Resource value chain overview.",
                ),
                BodyBlock(kind="paragraph", text="Hydrocarbons support industrialisation."),
                BodyBlock(kind="list_item", text="Power generation"),
                BodyBlock(kind="list_item", text="Petrochemicals"),
                BodyBlock(kind="paragraph", text="Long-term development depends on governance."),
            ],
            outline_body_indices=(0, 2, 5),
        )

        markdown = render_markdown_chapter(
            chapter,
            figure_image_map={1: ["![Figure 001](../images/figure-001.png)"]},
        )

        self.assertEqual(
            markdown,
            "\n".join(
                [
                    "# Chapter 1: General Introduction",
                    "",
                    "## 1.1- Hydrocarbon Resources",
                    "",
                    "West Africa has significant resources.",
                    "",
                    "![Figure 001](../images/figure-001.png)",
                    "",
                    "Figure 1: Resource value chain overview.",
                    "",
                    "### 1.1.1- Contribution to Growth",
                    "",
                    "Hydrocarbons support industrialisation.",
                    "",
                    "- Power generation",
                    "- Petrochemicals",
                    "",
                    "## 1.2- Future Potential",
                    "",
                    "Long-term development depends on governance.",
                    "",
                ]
            ),
        )

    def test_inserts_figure_images_for_colonless_captions(self) -> None:
        chapter = ChapterSemanticModel(
            source_path="editions/en/content/chapters/chapter-12-vision-for-west-africa-2050.md",
            title="Chapter 12: Vision for West Africa 2050",
            body=[
                BodyBlock(
                    kind="caption",
                    text="Figure 80 African Petroleum Industrialisation Model",
                ),
                BodyBlock(kind="paragraph", text="Vision text."),
            ],
        )

        markdown = render_markdown_chapter(
            chapter,
            figure_image_map={80: ["![Figure 080](../images/figure-080.png)"]},
        )

        self.assertIn("![Figure 080](../images/figure-080.png)", markdown)

    def test_inserts_table_html_for_table_captions_when_table_map_is_available(self) -> None:
        chapter = ChapterSemanticModel(
            source_path="editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md",
            title="Chapter 5: Hydrocarbon Value Chain",
            body=[
                BodyBlock(
                    kind="caption",
                    text="Table 2 Estimated Hydrocarbon Resources in West Africa",
                ),
                BodyBlock(kind="paragraph", text="Follow-on paragraph."),
            ],
        )

        markdown = render_markdown_chapter(
            chapter,
            table_html_map={
                2: [(
                    "Table 2 Estimated Hydrocarbon Resources in West Africa",
                    [
                        "<table>",
                        "<caption><p>Table 2 Estimated Hydrocarbon Resources in West Africa</p></caption>",
                        "<thead>",
                        "<tr>",
                        "  <th><p>Country</p></th>",
                        "  <th><p>Crude Oil Reserves (MMbbl)</p></th>",
                        "</tr>",
                        "</thead>",
                        "<tbody>",
                        "<tr>",
                        "  <td><p>Nigeria</p></td>",
                        "  <td><p>30,031*</p></td>",
                        "</tr>",
                        "</tbody>",
                        "</table>",
                    ],
                )]
            },
        )

        self.assertIn("<table>", markdown)
        self.assertIn("<caption><p>Table 2 Estimated Hydrocarbon Resources in West Africa</p></caption>", markdown)
        self.assertIn("<td><p>Nigeria</p></td>", markdown)
        self.assertNotIn("\nTable 2 Estimated Hydrocarbon Resources in West Africa\n\n", markdown)

    def test_does_not_consume_table_html_when_caption_text_only_matches_number(self) -> None:
        chapter = ChapterSemanticModel(
            source_path="editions/en/content/chapters/preface.md",
            title="Preface",
            body=[
                BodyBlock(
                    kind="caption",
                    text="Table 3 Daily Oil Production by Country (Trading Economics, 2025)184",
                ),
                BodyBlock(
                    kind="caption",
                    text="Table 3 Daily Oil Production by Country (Trading Economics, 2025)",
                ),
            ],
        )

        markdown = render_markdown_chapter(
            chapter,
            table_html_map={
                3: [(
                    "Table 3 Daily Oil Production by Country (Trading Economics, 2025)",
                    [
                        "<table>",
                        "<caption><p>Table 3 Daily Oil Production by Country (Trading Economics, 2025)</p></caption>",
                        "<thead>",
                        "<tr>",
                        "  <th><p>Country</p></th>",
                        "  <th><p>Reference Period</p></th>",
                        "</tr>",
                        "</thead>",
                        "<tbody>",
                        "</tbody>",
                        "</table>",
                    ],
                )]
            },
        )

        self.assertIn("Table 3 Daily Oil Production by Country (Trading Economics, 2025)184", markdown)
        self.assertIn("<table>", markdown)
        self.assertIn("Reference Period", markdown)

    def test_renders_standalone_strong_paragraphs_with_markdown_emphasis(self) -> None:
        chapter = ChapterSemanticModel(
            source_path="editions/en/content/chapters/chapter-05-hydrocarbon-value-chain.md",
            title="Chapter 5: Hydrocarbon Value Chain",
            body=[
                BodyBlock(kind="paragraph", text="Exploration", strong=True),
                BodyBlock(
                    kind="paragraph",
                    text="Exploration involves identifying hydrocarbon accumulations.",
                ),
                BodyBlock(kind="paragraph", text="High Geological Risk", strong=True),
                BodyBlock(
                    kind="paragraph",
                    text="Exploration activities involve significant geological uncertainty.",
                ),
            ],
        )

        markdown = render_markdown_chapter(chapter)

        self.assertIn("**Exploration**", markdown)
        self.assertIn("**High Geological Risk**", markdown)
        self.assertNotIn("****Exploration****", markdown)


if __name__ == "__main__":
    unittest.main()
