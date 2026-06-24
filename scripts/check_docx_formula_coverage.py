from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.check_docx_parity import _extract_aligned_docx_book
from scripts.docx_parity import extract_markdown_book
from scripts.docx_parity.model import BookSemanticModel
from scripts.docx_parity.normalize import normalize_formula_text, normalize_visible_text
from scripts.edition_config import available_edition_locales, get_edition


FORMULA_CONTAINER_START_RE = re.compile(
    r'<(?:div|section)\b[^>]*class="[^"]*'
    r'(?:book-formula|formula-group|formula-panel|formula-derivation|api-density-formula)'
    r'[^"]*"',
    re.IGNORECASE,
)
FORMULA_CONTAINER_END_RE = re.compile(r"</(?:div|section)>", re.IGNORECASE)
VISIBLE_WORD_RE = re.compile(r"[A-Za-z0-9°%]+")
MULTIPLICATIVE_TERM_RE = re.compile(
    r"(?:\d+(?:[.,]\d+)?x[a-z]|[a-z]\d*x\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FormulaCoverageDiff:
    chapter_path: str
    docx_value: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that DOCX formulas are rendered inside semantic formula blocks."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--chapter", help="Limit validation to a single Markdown chapter path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _normalize_formula_match_text(value: str) -> str:
    unescaped = html.unescape(value)
    unescaped = (
        unescaped.replace("ϕ", "phi")
        .replace("φ", "phi")
        .replace("Φ", "phi")
        .replace("Ø", "phi")
    )
    return normalize_formula_text(unescaped).lower()


def is_formula_candidate(text: str) -> bool:
    visible = normalize_visible_text(text)
    compact = _normalize_formula_match_text(text)
    if not visible or not compact:
        return False

    word_count = len(VISIBLE_WORD_RE.findall(visible))
    has_assignment = "=" in compact
    has_summation = "∑" in compact
    has_multiplicative_term = bool(MULTIPLICATIVE_TERM_RE.search(compact))
    has_letters = bool(re.search(r"[a-z]", compact))
    starts_with_numeric_result = compact.startswith("=") and bool(re.search(r"\d", compact))

    if not has_letters and not starts_with_numeric_result:
        return False
    if not has_assignment and not has_summation and not has_multiplicative_term:
        return False
    if word_count > 16:
        return False

    if has_assignment:
        return True

    if has_summation:
        return True

    return has_multiplicative_term and word_count <= 12 and not visible.endswith(
        (".", ":", ";")
    )


def _extract_formula_render_blob(chapter_path: Path) -> str:
    depth = 0
    captured: list[str] = []

    for line in chapter_path.read_text(encoding="utf-8").splitlines():
        depth += len(FORMULA_CONTAINER_START_RE.findall(line))
        if depth > 0:
            captured.append(line)
        if depth > 0:
            depth = max(0, depth - len(FORMULA_CONTAINER_END_RE.findall(line)))

    return _normalize_formula_match_text(" ".join(captured))


def find_formula_coverage_diffs(docx_book: BookSemanticModel) -> list[FormulaCoverageDiff]:
    diffs: list[FormulaCoverageDiff] = []

    for chapter in docx_book.chapters:
        chapter_path = Path(chapter.source_path)
        if not chapter_path.exists():
            continue

        formula_render_blob = _extract_formula_render_blob(chapter_path)
        seen: set[str] = set()

        for block in chapter.body:
            if block.kind != "paragraph" or not is_formula_candidate(block.text):
                continue

            normalized = _normalize_formula_match_text(block.text)
            if normalized in seen:
                continue
            seen.add(normalized)

            if normalized not in formula_render_blob:
                diffs.append(
                    FormulaCoverageDiff(
                        chapter_path=str(chapter_path),
                        docx_value=block.text,
                    )
                )

    return diffs


def _render_text_report(diffs: list[FormulaCoverageDiff]) -> str:
    lines = ["Missing semantic formula renderings:"]
    for diff in diffs:
        lines.append(f"- {diff.chapter_path}: {diff.docx_value}")
    return "\n".join(lines)


def _load_aligned_docx_book(args: argparse.Namespace) -> BookSemanticModel:
    edition = get_edition(args.edition) if args.edition else None
    docx_path = Path(args.docx) if args.docx else edition.docx_path if edition else None
    summary_path = Path(args.summary) if args.summary else edition.summary_path if edition else None
    chapters_dir = (
        Path(args.chapters_dir) if args.chapters_dir else edition.chapter_root if edition else None
    )

    if docx_path is None or summary_path is None or chapters_dir is None:
        raise SystemExit(
            "check_docx_formula_coverage requires either --edition or explicit --docx, --summary, and --chapters-dir."
        )

    markdown_book = extract_markdown_book(summary_path, chapters_dir)
    aligned_docx_book = _extract_aligned_docx_book(docx_path, markdown_book.chapters)

    if not args.chapter:
        return aligned_docx_book

    target_path = str(Path(args.chapter).resolve())
    filtered = [
        chapter for chapter in aligned_docx_book.chapters if chapter.source_path == target_path
    ]
    if not filtered:
        raise SystemExit(f"No Markdown chapter matched {args.chapter}")

    return BookSemanticModel(chapters=filtered)


def main() -> int:
    args = parse_args()
    docx_book = _load_aligned_docx_book(args)
    diffs = find_formula_coverage_diffs(docx_book)
    if diffs:
        if args.json:
            print(json.dumps([asdict(diff) for diff in diffs], ensure_ascii=False, indent=2))
        else:
            print(_render_text_report(diffs))
        return 1

    print("DOCX formula coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
