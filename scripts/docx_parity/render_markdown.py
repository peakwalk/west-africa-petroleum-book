from __future__ import annotations

import html
import re

from .model import BodyBlock, ChapterSemanticModel, OutlineEntry

FIGURE_RE = re.compile(r"^Figure\s+(?P<number>\d+)\s*:?\s*", re.IGNORECASE)
TABLE_RE = re.compile(r"^(?:Table|Tableau)\s+(?P<number>\d+)\s*:?\s*", re.IGNORECASE)


def _normalize_table_caption(text: str) -> str:
    normalized = html.unescape(text).replace("\u00a0", " ")
    normalized = re.sub(
        r"^((?:Table|Tableau)\s+\d+)[.:]?\s*",
        r"\1 ",
        normalized,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", normalized).strip()


def _render_heading(outline: OutlineEntry) -> list[str]:
    return [f"{'#' * outline.level} {outline.number} {outline.title}", ""]


def _render_block(
    block: BodyBlock,
    figure_image_map: dict[int, list[str]],
    table_html_map: dict[int, list[tuple[str, list[str]]]],
) -> list[str]:
    rendered: list[str] = []
    figure_match = FIGURE_RE.match(block.text)
    if block.kind == "caption" and figure_match is not None:
        figure_number = int(figure_match.group("number"))
        for image_line in figure_image_map.get(figure_number, []):
            rendered.append(image_line)
            rendered.append("")
        rendered.append(block.text)
        rendered.append("")
        return rendered

    table_match = TABLE_RE.match(block.text)
    if block.kind == "caption" and table_match is not None:
        table_number = int(table_match.group("number"))
        table_entries = table_html_map.get(table_number, [])
        normalized_caption = _normalize_table_caption(block.text)
        matching_index = next(
            (
                index
                for index, (caption_text, _) in enumerate(table_entries)
                if _normalize_table_caption(caption_text) == normalized_caption
            ),
            None,
        )
        if matching_index is not None:
            _, table_lines = table_entries.pop(matching_index)
            rendered.extend(table_lines)
            rendered.append("")
            return rendered
        rendered.append(block.text)
        rendered.append("")
        return rendered

    if block.kind == "list_item":
        return [f"- {block.text}"]

    rendered.append(f"**{block.text}**" if block.kind == "paragraph" and block.strong else block.text)
    rendered.append("")
    return rendered


def render_markdown_chapter(
    chapter: ChapterSemanticModel,
    *,
    figure_image_map: dict[int, list[str]] | None = None,
    table_html_map: dict[int, list[tuple[str, list[str]]]] | None = None,
) -> str:
    figure_image_map = figure_image_map or {}
    table_html_map = table_html_map or {}
    insertion_map: dict[int, list[OutlineEntry]] = {}
    for body_index, outline in zip(chapter.outline_body_indices, chapter.outline):
        insertion_map.setdefault(body_index, []).append(outline)

    rendered: list[str] = [f"# {chapter.title}", ""]
    previous_block_kind: str | None = None

    for block_index, block in enumerate(chapter.body):
        if previous_block_kind == "list_item" and (
            insertion_map.get(block_index) or block.kind != "list_item"
        ):
            rendered.append("")

        for outline in insertion_map.get(block_index, []):
            rendered.extend(_render_heading(outline))

        rendered.extend(_render_block(block, figure_image_map, table_html_map))
        previous_block_kind = block.kind

    for outline in insertion_map.get(len(chapter.body), []):
        if previous_block_kind == "list_item":
            rendered.append("")
        rendered.extend(_render_heading(outline))

    return "\n".join(rendered).rstrip() + "\n"
