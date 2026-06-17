from .model import BookSemanticModel, ParityDiff


def compare_books(docx_book: BookSemanticModel, markdown_book: BookSemanticModel) -> list[ParityDiff]:
    diffs: list[ParityDiff] = []

    if len(docx_book.chapters) != len(markdown_book.chapters):
        diffs.append(
            ParityDiff(
                chapter_path="editions/en/content/SUMMARY.md",
                diff_type="outline.chapter_count_mismatch",
                docx_value=str(len(docx_book.chapters)),
                markdown_value=str(len(markdown_book.chapters)),
                hint="Align SUMMARY chapter coverage with the reference DOCX before comparing chapter bodies.",
            )
        )

    for docx_chapter, markdown_chapter in zip(docx_book.chapters, markdown_book.chapters):
        if docx_chapter.title != markdown_chapter.title:
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="outline.chapter_title_mismatch",
                    docx_value=docx_chapter.title,
                    markdown_value=markdown_chapter.title,
                    hint="Align the chapter title with the reference DOCX.",
                )
            )

        if len(docx_chapter.outline) != len(markdown_chapter.outline):
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="outline.entry_count_mismatch",
                    docx_value=str(len(docx_chapter.outline)),
                    markdown_value=str(len(markdown_chapter.outline)),
                    hint="Align the number of section headings in this chapter before checking individual labels.",
                )
            )

        for docx_outline, markdown_outline in zip(docx_chapter.outline, markdown_chapter.outline):
            if docx_outline.level != markdown_outline.level:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.level_mismatch",
                        docx_value=f"L{docx_outline.level} {docx_outline.number} {docx_outline.title}",
                        markdown_value=f"L{markdown_outline.level} {markdown_outline.number} {markdown_outline.title}",
                        hint="Restore the heading depth so DOCX and Markdown use the same section hierarchy.",
                    )
                )
            if docx_outline.number != markdown_outline.number:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.number_mismatch",
                        docx_value=f"{docx_outline.number} {docx_outline.title}",
                        markdown_value=f"{markdown_outline.number} {markdown_outline.title}",
                        hint="Promote this item to a real section heading and preserve the DOCX numbering label.",
                    )
                )
            if docx_outline.title != markdown_outline.title:
                diffs.append(
                    ParityDiff(
                        chapter_path=markdown_chapter.source_path,
                        diff_type="outline.title_text_mismatch",
                        docx_value=docx_outline.title,
                        markdown_value=markdown_outline.title,
                        hint="Match the visible heading text to the reference DOCX.",
                    )
                )

        if len(docx_chapter.body) != len(markdown_chapter.body):
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="body.block_count_mismatch",
                    docx_value=str(len(docx_chapter.body)),
                    markdown_value=str(len(markdown_chapter.body)),
                    hint="Align the number of visible paragraph/list/caption blocks before checking sequence content.",
                )
            )

        docx_sequence = [(block.kind, block.text) for block in docx_chapter.body]
        markdown_sequence = [(block.kind, block.text) for block in markdown_chapter.body]
        if docx_sequence != markdown_sequence:
            diffs.append(
                ParityDiff(
                    chapter_path=markdown_chapter.source_path,
                    diff_type="body.sequence_mismatch",
                    docx_value=" | ".join(f"{kind}:{text}" for kind, text in docx_sequence[:5]),
                    markdown_value=" | ".join(f"{kind}:{text}" for kind, text in markdown_sequence[:5]),
                    hint="Compare the visible paragraph/list/caption sequence and repair the first drift point.",
                )
            )

    return diffs
