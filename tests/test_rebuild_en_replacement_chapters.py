from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.docx_parity.model import BodyBlock, ChapterSemanticModel
from scripts.rebuild_en_replacement_chapters import build_rendered_outputs


class RebuildEnglishReplacementChaptersTests(unittest.TestCase):
    def test_build_rendered_outputs_includes_front_and_back_matter(self) -> None:
        markdown_chapters = [
            ChapterSemanticModel(
                source_path="/tmp/chapters/disclaimer.md",
                title="DISCLAIMER",
            ),
            ChapterSemanticModel(
                source_path="/tmp/chapters/chapter-01-general-introduction.md",
                title="Chapter 1: General Introduction",
            ),
            ChapterSemanticModel(
                source_path="/tmp/chapters/glossary.md",
                title="Glossary",
            ),
        ]
        docx_chapters = [
            ChapterSemanticModel(
                source_path="docx:1",
                title="DISCLAIMER",
                body=[BodyBlock(kind="paragraph", text="Disclaimer text.", strong=True)],
            ),
            ChapterSemanticModel(
                source_path="docx:2",
                title="Chapter 1: General Introduction",
                body=[BodyBlock(kind="paragraph", text="Intro text.")],
            ),
            ChapterSemanticModel(
                source_path="docx:3",
                title="Glossary",
                body=[BodyBlock(kind="paragraph", text="Glossary text.")],
            ),
        ]

        with patch(
            "scripts.rebuild_en_replacement_chapters.extract_markdown_book",
            return_value=SimpleNamespace(chapters=markdown_chapters),
        ), patch(
            "scripts.rebuild_en_replacement_chapters.extract_docx_book",
            return_value=SimpleNamespace(chapters=docx_chapters),
        ), patch(
            "scripts.rebuild_en_replacement_chapters._figure_image_map",
            return_value={},
        ), patch(
            "scripts.rebuild_en_replacement_chapters._table_html_map",
            return_value={},
        ):
            outputs = build_rendered_outputs(
                Path("/tmp/reference.docx"),
                Path("/tmp/SUMMARY.md"),
                Path("/tmp/chapters"),
            )

        self.assertEqual(
            [path.name for path, _ in outputs],
            [
                "disclaimer.md",
                "chapter-01-general-introduction.md",
                "glossary.md",
            ],
        )
        self.assertIn("**Disclaimer text.**", outputs[0][1])

    def test_build_rendered_outputs_restores_chapter_6_volumetric_formula_semantics(self) -> None:
        markdown_chapters = [
            ChapterSemanticModel(
                source_path="/tmp/chapters/chapter-06-upstream-operations-and-government-roles.md",
                title="Upstream Operations and Government Roles",
            )
        ]
        docx_chapters = [
            ChapterSemanticModel(
                source_path="docx:6",
                title="Upstream Operations and Government Roles",
                body=[
                    BodyBlock(
                        kind="paragraph",
                        text="Because considerable uncertainty exists, volumetric estimates are generally expressed as probabilistic ranges.",
                    ),
                    BodyBlock(kind="paragraph", text="VHcP=GRV×N/G×ϕ×Shc×1/FVF"),
                    BodyBlock(kind="paragraph", text="Where:"),
                    BodyBlock(
                        kind="paragraph",
                        text="GRV (Gross Rock Volume) - the gross volume of the reservoir rock. It is determined from the geometric shape and thickness of the reservoir.",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="GRV=∑(ReservoirArea×ReservoirThickness)",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="N/G (Net-to-Gross Ratio) - the ratio of net reservoir thickness to gross reservoir thickness. Reservoir intervals rarely exhibit uniform lithology and are often interbedded with impermeable shale layers.",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="φ (Phi) - Reservoir Porosity - estimated from well logs, core measurements, and analogue reservoir data. It is defined as:",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="ϕ=PoreVolume(Vv)/BulkReservoirVolume(V)",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="Shc (Hydrocarbon Saturation) - determined from the water saturation (Sw). It is generally calculated from well log data within the effective porosity interval.",
                    ),
                    BodyBlock(kind="paragraph", text="Shc=1-Sw"),
                    BodyBlock(
                        kind="paragraph",
                        text="FVF (Formation Volume Factor) - expresses the change in fluid volume between reservoir conditions and standard surface conditions (pressure = 1 atmosphere and temperature = 15°C). For oil, the formation volume factor is represented by Bo, while for gas it is represented by Bg.",
                    ),
                    BodyBlock(kind="paragraph", text="FVF=ReservoirVolume/SurfaceVolume"),
                    BodyBlock(kind="paragraph", text="Oil Volumes", strong=True),
                    BodyBlock(kind="paragraph", text="For oil:"),
                    BodyBlock(kind="paragraph", text="FVF=Bo"),
                    BodyBlock(kind="paragraph", text="Shc=So"),
                    BodyBlock(kind="paragraph", text="where So is the oil saturation."),
                    BodyBlock(kind="paragraph", text="Therefore:"),
                    BodyBlock(kind="paragraph", text="STOIIP=GRV×N/G×ϕ×So×1/Bo"),
                    BodyBlock(
                        kind="paragraph",
                        text="The volume of associated gas in place is calculated as:",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="AssociatedGasInPlace=STOIIP×GOR",
                    ),
                    BodyBlock(kind="paragraph", text="Gas Volumes", strong=True),
                    BodyBlock(kind="paragraph", text="For gas:"),
                    BodyBlock(kind="paragraph", text="FVF=Bg"),
                    BodyBlock(kind="paragraph", text="Shc=Sg"),
                    BodyBlock(kind="paragraph", text="where Sg is the gas saturation."),
                    BodyBlock(kind="paragraph", text="Therefore:"),
                    BodyBlock(kind="paragraph", text="GIIP=GRV×N/G×ϕ×Sg×1/Bg"),
                    BodyBlock(
                        kind="paragraph",
                        text="The volume of condensate in place is calculated as:",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="CondensateInPlace=GIIP×CGR",
                    ),
                    BodyBlock(kind="paragraph", text="Where:"),
                    BodyBlock(
                        kind="paragraph",
                        text="GOR (Gas-Oil Ratio) - the ratio of produced gas volume to produced oil volume.",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="CGR (Condensate-Gas Ratio) - the ratio of produced condensate volume to produced gas volume.",
                    ),
                    BodyBlock(
                        kind="paragraph",
                        text="The overall Geological Chance of Success is calculated as:",
                    ),
                    BodyBlock(kind="paragraph", text="GCoS = Ps × Pr × Pse × Pt"),
                    BodyBlock(kind="paragraph", text="For example:"),
                    BodyBlock(kind="paragraph", text="GCoS = 0.90 × 0.80 × 0.85 × 0.90"),
                    BodyBlock(kind="paragraph", text="= 0.55 (55%)"),
                ],
            )
        ]

        with patch(
            "scripts.rebuild_en_replacement_chapters.extract_markdown_book",
            return_value=SimpleNamespace(chapters=markdown_chapters),
        ), patch(
            "scripts.rebuild_en_replacement_chapters.extract_docx_book",
            return_value=SimpleNamespace(chapters=docx_chapters),
        ), patch(
            "scripts.rebuild_en_replacement_chapters._figure_image_map",
            return_value={},
        ), patch(
            "scripts.rebuild_en_replacement_chapters._table_html_map",
            return_value={},
        ):
            outputs = build_rendered_outputs(
                Path("/tmp/reference.docx"),
                Path("/tmp/SUMMARY.md"),
                Path("/tmp/chapters"),
            )

        self.assertEqual([path.name for path, _ in outputs], ["chapter-06-upstream-operations-and-government-roles.md"])
        self.assertIn('class="formula-group formula-group--volumetric"', outputs[0][1])
        self.assertIn('data-equation-label="6.1"', outputs[0][1])
        self.assertIn("VHcP = GRV × N/G × ϕ × Shc × 1/FVF", outputs[0][1])
        self.assertIn("class=\"formula-case-title\">Oil Volumes</p>", outputs[0][1])
        self.assertIn(">For Oil</p>", outputs[0][1])
        self.assertIn("The volume of associated gas in place is calculated as:", outputs[0][1])
        self.assertIn("STOIIP = GRV × N/G × ϕ × So × 1/Bo", outputs[0][1])
        self.assertIn('data-equation-label="6.2"', outputs[0][1])
        self.assertIn('data-equation-label="6.3"', outputs[0][1])
        self.assertIn(
            'aria-label="GCoS equals 0.90 times 0.80 times 0.85 times 0.90 and equals 0.55 or 55 percent"',
            outputs[0][1],
        )


if __name__ == "__main__":
    unittest.main()
