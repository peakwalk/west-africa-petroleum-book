import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
from scripts.docx_parity import (
    compare_books,
    extract_docx_book,
    extract_docx_chapter_by_anchors,
    extract_markdown_book,
    render_json_report,
    render_text_report,
)
from scripts.docx_parity.model import BookSemanticModel, ChapterSemanticModel
from scripts.docx_parity.normalize import normalize_visible_text, split_heading_label


HEADING_RE = re.compile(r"^#{2,6}\s+(?P<content>.+)$")
DOCX_CHAPTER_TITLE_RE = re.compile(
    r"^(?:Chapter|Chapitre)\s+\d+\s*:\s*(?P<title>.+)$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Markdown semantic parity against the reference DOCX."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--chapter", help="Limit validation to a single Markdown chapter path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def chapter_anchor(chapter) -> str:
    source_path = Path(chapter.source_path)
    if source_path.exists():
        in_parity_ignore = False
        seen_title = False
        lines = source_path.read_text(encoding="utf-8").splitlines()
        index = 0
        first_heading_title: str | None = None
        while index < len(lines):
            raw_line = lines[index]
            stripped = raw_line.strip()
            if not seen_title:
                if stripped.startswith("# "):
                    seen_title = True
                index += 1
                continue
            if stripped == "<!-- parity-ignore:start -->":
                in_parity_ignore = True
                index += 1
                continue
            if stripped == "<!-- parity-ignore:end -->":
                in_parity_ignore = False
                index += 1
                continue
            if in_parity_ignore or not stripped or stripped.startswith("!["):
                index += 1
                continue
            heading_match = HEADING_RE.match(stripped)
            if heading_match:
                _, title = split_heading_label(heading_match.group("content"))
                if first_heading_title is None:
                    first_heading_title = title
                index += 1
                continue
            block_lines = [stripped]
            index += 1
            while index < len(lines):
                candidate = lines[index].strip()
                if (
                    not candidate
                    or candidate == "<!-- parity-ignore:start -->"
                    or candidate == "<!-- parity-ignore:end -->"
                    or candidate.startswith("![")
                    or HEADING_RE.match(candidate)
                ):
                    break
                block_lines.append(candidate)
                index += 1
            return normalize_visible_text(" ".join(block_lines))
        if first_heading_title:
            return first_heading_title
    if chapter.body:
        return chapter.body[0].text
    if chapter.outline:
        return chapter.outline[0].title
    return chapter.title


def _include_in_docx_expected_titles(chapter) -> bool:
    source_name = Path(chapter.source_path).name
    if source_name.startswith("chapter-"):
        return True
    return source_name in {
        "disclaimer.md",
        "glossary.md",
        "bibliographical-references.md",
    }


def _docx_expected_title(title: str) -> str:
    match = DOCX_CHAPTER_TITLE_RE.match(normalize_visible_text(title))
    if match is not None:
        return normalize_visible_text(match.group("title"))
    return normalize_visible_text(title)


def _docx_expected_titles(chapters) -> list[str]:
    return [
        _docx_expected_title(chapter.title)
        for chapter in chapters
        if _include_in_docx_expected_titles(chapter)
    ]


def _extract_aligned_docx_book(
    docx_path: Path,
    markdown_chapters,
) -> BookSemanticModel:
    expected_markdown_chapters = [
        chapter for chapter in markdown_chapters if _include_in_docx_expected_titles(chapter)
    ]
    docx_book = extract_docx_book(
        docx_path,
        expected_titles=_docx_expected_titles(markdown_chapters),
    )
    aligned_chapters = [
        ChapterSemanticModel(
            source_path=markdown_chapter.source_path,
            title=markdown_chapter.title,
            outline=docx_chapter.outline,
            body=docx_chapter.body,
            outline_body_indices=docx_chapter.outline_body_indices,
        )
        for docx_chapter, markdown_chapter in zip(docx_book.chapters, expected_markdown_chapters)
    ]
    return BookSemanticModel(chapters=aligned_chapters)


def main() -> int:
    args = parse_args()
    edition = get_edition(args.edition) if args.edition else None
    docx_path = Path(args.docx) if args.docx else edition.docx_path if edition else None
    summary_path = Path(args.summary) if args.summary else edition.summary_path if edition else None
    chapters_dir = (
        Path(args.chapters_dir) if args.chapters_dir else edition.chapter_root if edition else None
    )

    if docx_path is None or summary_path is None or chapters_dir is None:
        raise SystemExit(
            "check_docx_parity requires either --edition or explicit --docx, --summary, and --chapters-dir."
        )

    all_markdown_book = extract_markdown_book(summary_path, chapters_dir)
    aligned_docx_book = _extract_aligned_docx_book(docx_path, all_markdown_book.chapters)

    if args.chapter:
        target_path = str(Path(args.chapter).resolve())
        markdown_chapters = [
            chapter for chapter in all_markdown_book.chapters if chapter.source_path == target_path
        ]
        if not markdown_chapters:
            print(f"No Markdown chapter matched {args.chapter}")
            return 1
        markdown_book = type(all_markdown_book)(chapters=markdown_chapters)
        docx_chapters = [
            chapter for chapter in aligned_docx_book.chapters if chapter.source_path == target_path
        ]
        if docx_chapters and docx_chapters[0].body:
            docx_book = BookSemanticModel(chapters=docx_chapters)
        else:
            target_index = next(
                index
                for index, chapter in enumerate(all_markdown_book.chapters)
                if chapter.source_path == target_path
            )
            next_anchor = None
            if target_index + 1 < len(all_markdown_book.chapters):
                next_anchor = chapter_anchor(all_markdown_book.chapters[target_index + 1])
            docx_book = extract_docx_chapter_by_anchors(
                docx_path,
                chapter_title=markdown_chapters[0].title,
                start_anchor=chapter_anchor(markdown_chapters[0]),
                end_anchor=next_anchor,
            )
    else:
        markdown_chapters = [
            chapter
            for chapter in all_markdown_book.chapters
            if Path(chapter.source_path).name.startswith("chapter-")
        ]
        markdown_book = type(all_markdown_book)(chapters=markdown_chapters)
        docx_book = BookSemanticModel(
            chapters=[
                chapter
                for chapter in aligned_docx_book.chapters
                if Path(chapter.source_path).name.startswith("chapter-")
            ]
        )

    diffs = compare_books(docx_book, markdown_book)
    if diffs:
        print(render_json_report(diffs) if args.json else render_text_report(diffs))
        return 1

    print("DOCX parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
