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
                source_path="/tmp/chapters/preface.md",
                title="Preface",
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
                title="Preface",
                body=[BodyBlock(kind="paragraph", text="Preface text.")],
            ),
            ChapterSemanticModel(
                source_path="docx:4",
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
                "preface.md",
                "glossary.md",
            ],
        )
        self.assertIn("**Disclaimer text.**", outputs[0][1])


if __name__ == "__main__":
    unittest.main()
