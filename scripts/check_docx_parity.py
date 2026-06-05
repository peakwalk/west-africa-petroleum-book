import argparse
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_parity import (
    compare_books,
    extract_docx_book,
    extract_docx_chapter_by_anchors,
    extract_markdown_book,
    render_json_report,
    render_text_report,
)
from scripts.docx_parity.normalize import normalize_visible_text, split_heading_label


HEADING_RE = re.compile(r"^#{2,6}\s+(?P<content>.+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Markdown semantic parity against the reference DOCX."
    )
    parser.add_argument("--docx", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--chapters-dir", required=True)
    parser.add_argument("--chapter", help="Limit validation to a single Markdown chapter path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markdown_book = extract_markdown_book(Path(args.summary), Path(args.chapters_dir))

    def chapter_anchor(chapter) -> str:
        source_path = Path(chapter.source_path)
        if source_path.exists():
            in_parity_ignore = False
            seen_title = False
            lines = source_path.read_text(encoding="utf-8").splitlines()
            index = 0
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
                    return title
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
        if chapter.body:
            return chapter.body[0].text
        if chapter.outline:
            return chapter.outline[0].title
        return chapter.title

    if args.chapter:
        target_path = str(Path(args.chapter).resolve())
        markdown_chapters = [
            chapter for chapter in markdown_book.chapters if chapter.source_path == target_path
        ]
        if not markdown_chapters:
            print(f"No Markdown chapter matched {args.chapter}")
            return 1
        markdown_book = type(markdown_book)(chapters=markdown_chapters)
        all_markdown_chapters = extract_markdown_book(
            Path(args.summary), Path(args.chapters_dir)
        )
        target_index = next(
            index
            for index, chapter in enumerate(all_markdown_chapters.chapters)
            if chapter.source_path == target_path
        )

        next_anchor = None
        if target_index + 1 < len(all_markdown_chapters.chapters):
            next_anchor = chapter_anchor(all_markdown_chapters.chapters[target_index + 1])

        docx_book = extract_docx_chapter_by_anchors(
            Path(args.docx),
            chapter_title=markdown_chapters[0].title,
            start_anchor=chapter_anchor(markdown_chapters[0]),
            end_anchor=next_anchor,
        )
    else:
        markdown_chapters = [
            chapter
            for chapter in markdown_book.chapters
            if Path(chapter.source_path).name.startswith("chapter-")
        ]
        markdown_book = type(markdown_book)(chapters=markdown_chapters)
        docx_chapters = []
        for index, chapter in enumerate(markdown_chapters):
            next_anchor = None
            if index + 1 < len(markdown_chapters):
                next_anchor = chapter_anchor(markdown_chapters[index + 1])
            extracted = extract_docx_chapter_by_anchors(
                Path(args.docx),
                chapter_title=chapter.title,
                start_anchor=chapter_anchor(chapter),
                end_anchor=next_anchor,
            )
            docx_chapters.extend(extracted.chapters)
        docx_book = type(markdown_book)(chapters=docx_chapters)

    diffs = compare_books(docx_book, markdown_book)
    if diffs:
        print(render_json_report(diffs) if args.json else render_text_report(diffs))
        return 1

    print("DOCX parity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
