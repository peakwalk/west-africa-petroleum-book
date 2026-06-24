from __future__ import annotations

import html
import re
from pathlib import Path

from .model import BodyBlock, BookSemanticModel, ChapterSemanticModel, OutlineEntry
from .normalize import is_caption_text, normalize_formula_text, normalize_visible_text, split_heading_label

SUMMARY_LINK_RE = re.compile(r"^\s*-\s+\[(?P<title>.+?)\]\((?P<path>.+?)\)\s*$")
LIST_ITEM_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+(?P<text>.+)$")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
HTML_TAG_RE = re.compile(r"<[^>]+>")
FENCE_RE = re.compile(r"^```(?:\s*(?P<lang>[A-Za-z0-9_+-]+))?\s*$")
PARITY_IGNORE_START = "<!-- parity-ignore:start -->"
PARITY_IGNORE_END = "<!-- parity-ignore:end -->"
FIGURE_LABEL_MAX_WORDS = 6
STANDALONE_STRONG_RE = re.compile(r"^\s*(\*\*|__)(?P<content>.+?)\1\s*$")


def _summary_entries(summary_path: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for raw_line in summary_path.read_text(encoding="utf-8").splitlines():
        match = SUMMARY_LINK_RE.match(raw_line)
        if not match:
            continue
        relative_path = Path(match.group("path"))
        chapter_path = (summary_path.parent / relative_path).resolve()
        entries.append((match.group("title"), chapter_path))
    return entries


def _strip_ignored_regions(lines: list[str]) -> list[str]:
    kept: list[str] = []
    ignoring = False
    for line in lines:
        if PARITY_IGNORE_START in line:
            ignoring = True
            continue
        if PARITY_IGNORE_END in line:
            ignoring = False
            continue
        if not ignoring:
            kept.append(line)
    return kept


def _is_short_figure_label(text: str) -> bool:
    normalized = normalize_visible_text(text)
    words = normalized.split()
    return 0 < len(words) <= FIGURE_LABEL_MAX_WORDS and not any(
        punctuation in normalized for punctuation in ".!?:;"
    )


def _looks_like_semantic_callout(text: str) -> bool:
    normalized = normalize_visible_text(text)
    if "," in normalized:
        return True

    words = normalized.split()
    if len(words) < 3:
        return False

    return all(re.fullmatch(r"[A-Z][A-Z0-9/&()'.-]*", word) for word in words)


def _strip_html_tags(text: str) -> str:
    return normalize_visible_text(html.unescape(HTML_TAG_RE.sub(" ", text)))


def _parse_chapter(chapter_path: Path) -> ChapterSemanticModel:
    lines = _strip_ignored_regions(chapter_path.read_text(encoding="utf-8").splitlines())
    title = ""
    outline: list[OutlineEntry] = []
    body: list[BodyBlock] = []
    paragraph_lines: list[str] = []
    seen_outline = False
    suppress_pre_heading_figure_labels = False
    suppress_figure_labels = False
    ignoring_html_table = False
    capturing_html_caption = False
    html_caption_lines: list[str] = []
    html_table_lines: list[str] = []
    active_fence_lang: str | None = None
    fence_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal suppress_figure_labels
        if not paragraph_lines:
            return
        raw_text = " ".join(paragraph_lines).strip()
        strong_match = STANDALONE_STRONG_RE.fullmatch(raw_text)
        text = normalize_visible_text(raw_text)
        paragraph_lines.clear()
        if not text:
            return
        kind = "caption" if is_caption_text(text) else "paragraph"
        body.append(
            BodyBlock(
                kind=kind,
                text=text,
                strong=kind == "paragraph" and strong_match is not None,
            )
        )
        if kind == "caption":
            suppress_figure_labels = text.startswith("Figure ")

    def flush_fence() -> None:
        nonlocal active_fence_lang
        if active_fence_lang == "math":
            text = normalize_formula_text(" ".join(fence_lines))
            if text:
                body.append(BodyBlock(kind="paragraph", text=text))
        fence_lines.clear()
        active_fence_lang = None

    def next_nonempty_line(start_index: int) -> str:
        for candidate in lines[start_index + 1 :]:
            stripped_candidate = candidate.strip()
            if stripped_candidate:
                return stripped_candidate
        return ""

    for index, line in enumerate(lines):
        raw_line = line.rstrip("\n")
        stripped = line.strip()
        lowered = stripped.lower()
        fence_match = FENCE_RE.match(stripped)
        if active_fence_lang is not None:
            if fence_match:
                flush_fence()
            else:
                fence_lines.append(stripped)
            continue
        next_stripped = next_nonempty_line(index)
        if ignoring_html_table:
            html_table_lines.append(stripped)
            if "<caption" in lowered:
                capturing_html_caption = True
            if capturing_html_caption:
                cleaned = _strip_html_tags(stripped)
                if cleaned:
                    html_caption_lines.append(cleaned)
                if "</caption>" in lowered:
                    caption_text = normalize_visible_text(" ".join(html_caption_lines))
                    html_caption_lines.clear()
                    capturing_html_caption = False
                    if caption_text:
                        body.append(BodyBlock(kind="caption", text=caption_text))
            if "</table>" in lowered:
                ignoring_html_table = False
                capturing_html_caption = False
                html_caption_lines.clear()
                html_table_lines.clear()
            continue
        if fence_match:
            flush_paragraph()
            active_fence_lang = (fence_match.group("lang") or "").lower()
            fence_lines.clear()
            continue
        if not stripped:
            flush_paragraph()
            if body and body[-1].kind == "caption":
                suppress_figure_labels = False
            continue
        if (
            paragraph_lines
            and is_caption_text(paragraph_lines[0])
            and not stripped.startswith(("#", ">", "!["))
            and not LIST_ITEM_RE.match(stripped)
        ):
            paragraph_lines.append(stripped)
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            title = normalize_visible_text(stripped[2:])
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            flush_paragraph()
            continue
        if stripped.startswith(("## ", "### ", "#### ", "##### ", "###### ")):
            flush_paragraph()
            hashes, raw_heading = stripped.split(" ", 1)
            number, heading_title = split_heading_label(raw_heading)
            outline.append(OutlineEntry(level=len(hashes), number=number, title=heading_title))
            seen_outline = True
            suppress_pre_heading_figure_labels = False
            suppress_figure_labels = False
            continue
        if lowered.startswith("<table"):
            flush_paragraph()
            ignoring_html_table = True
            html_table_lines = [stripped]
            continue
        if stripped.startswith("<") and stripped.endswith(">"):
            cleaned_html = _strip_html_tags(stripped)
            if "formula" in lowered:
                flush_paragraph()
                if "book-formula-bridge" in lowered:
                    if cleaned_html and body and body[-1].kind == "paragraph":
                        body[-1] = BodyBlock(
                            kind="paragraph",
                            text=normalize_visible_text(f"{body[-1].text} {cleaned_html}"),
                        )
                    continue
                if cleaned_html:
                    kind = "paragraph"
                    text = cleaned_html
                    if "formula-case-title" in lowered:
                        kind = "list_item"
                    elif "formula-case-connector" in lowered and cleaned_html == "Thus":
                        text = "Thus,"
                    body.append(BodyBlock(kind=kind, text=text))
                continue
            if not cleaned_html:
                flush_paragraph()
                continue
        if stripped.startswith("<") and "formula" in lowered:
            flush_paragraph()
            cleaned_formula = _strip_html_tags(stripped)
            if cleaned_formula:
                body.append(BodyBlock(kind="paragraph", text=cleaned_formula))
            continue
        if TABLE_ROW_RE.match(stripped):
            flush_paragraph()
            continue
        list_match = LIST_ITEM_RE.match(stripped)
        if list_match:
            flush_paragraph()
            suppress_figure_labels = False
            body.append(
                BodyBlock(
                    kind="list_item",
                    text=normalize_visible_text(list_match.group("text")),
                )
            )
            continue
        if raw_line.startswith((" ", "\t")) and body and body[-1].kind == "list_item":
            merged = normalize_visible_text(f"{body[-1].text} {stripped}")
            body[-1] = BodyBlock(kind="list_item", text=merged)
            continue
        if stripped.startswith("!["):
            flush_paragraph()
            suppress_figure_labels = True
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            suppress_figure_labels = False
            body.append(
                BodyBlock(
                    kind="paragraph",
                    text=normalize_visible_text(stripped.lstrip("> ").strip()),
                )
            )
            continue
        if (
            _is_short_figure_label(stripped)
            and not is_caption_text(stripped)
            and not _looks_like_semantic_callout(stripped)
            and (
                suppress_figure_labels
                or next_stripped.startswith("![")
                or is_caption_text(next_stripped)
            )
        ):
            continue
        if (
            not seen_outline
            and suppress_pre_heading_figure_labels
            and _is_short_figure_label(stripped)
            and not _looks_like_semantic_callout(stripped)
        ):
            continue
        if is_caption_text(stripped):
            suppress_pre_heading_figure_labels = not seen_outline
            suppress_figure_labels = True
        elif suppress_figure_labels:
            suppress_figure_labels = False
        paragraph_lines.append(stripped)

    if active_fence_lang is not None:
        flush_fence()
    flush_paragraph()
    return ChapterSemanticModel(source_path=str(chapter_path), title=title, outline=outline, body=body)


def extract_markdown_book(
    summary_path: str | Path, chapters_dir: str | Path | None = None
) -> BookSemanticModel:
    summary_path = Path(summary_path)
    _ = chapters_dir
    chapters = [_parse_chapter(chapter_path) for _, chapter_path in _summary_entries(summary_path)]
    return BookSemanticModel(chapters=chapters)
