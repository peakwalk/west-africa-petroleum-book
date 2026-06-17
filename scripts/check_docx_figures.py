from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
from scripts.docx_figures import (
    FigureCoverageDiff,
    FigureObjectStats,
    FigureRecord,
    build_figure_inventory,
    render_figure_coverage_json,
    render_figure_coverage_text,
)
from scripts.docx_parity.normalize import normalize_visible_text

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("editions/en/content/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("editions/en/content/chapters")
DEFAULT_MANIFEST = Path("editions/en/content/images/figure-manifest.json")
SUMMARY_LINK_RE = re.compile(r"^\s*-\s+\[(?P<title>.+?)\]\((?P<path>.+?)\)\s*$")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")
FIGURE_PATH_RE = re.compile(r"figure-(?P<number>\d+)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Markdown and asset coverage for DOCX figure inventory."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--manifest")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _chapter_paths(summary_path: Path) -> list[Path]:
    chapter_paths: list[Path] = []
    for raw_line in summary_path.read_text(encoding="utf-8").splitlines():
        match = SUMMARY_LINK_RE.match(raw_line)
        if not match:
            continue
        relative_path = Path(match.group("path"))
        chapter_path = (summary_path.parent / relative_path).resolve()
        if chapter_path.name.startswith("chapter-"):
            chapter_paths.append(chapter_path)
    return chapter_paths


def _load_manifest(manifest_path: Path) -> list[FigureRecord]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    records: list[FigureRecord] = []
    for item in payload:
        objects = FigureObjectStats(**item["objects"])
        records.append(
            FigureRecord(
                number=item["number"],
                caption=item["caption"],
                chapter_title=item["chapter_title"],
                chapter_path=item["chapter_path"],
                caption_paragraph_index=item["caption_paragraph_index"],
                object_paragraph_start=item["object_paragraph_start"],
                object_paragraph_end=item["object_paragraph_end"],
                kind=item["kind"],
                objects=objects,
                published_assets=item.get("published_assets", []),
            )
        )
    return records


def _markdown_image_refs(chapter_paths: list[Path]) -> dict[int, list[tuple[str, str]]]:
    refs: dict[int, list[tuple[str, str]]] = {}
    for chapter_path in chapter_paths:
        content = chapter_path.read_text(encoding="utf-8")
        for match in MARKDOWN_IMAGE_RE.finditer(content):
            image_path = normalize_visible_text(match.group("path"))
            number_match = FIGURE_PATH_RE.search(Path(image_path).name)
            if number_match is None:
                continue
            number = int(number_match.group("number"))
            refs.setdefault(number, []).append((str(chapter_path), image_path))
    return refs


def _coverage_diffs(
    records: list[FigureRecord],
    markdown_refs: dict[int, list[tuple[str, str]]],
    images_root: Path,
) -> list[FigureCoverageDiff]:
    diffs: list[FigureCoverageDiff] = []
    record_by_number = {record.number: record for record in records}

    for record in records:
        refs = markdown_refs.get(record.number, [])
        if not refs:
            diffs.append(
                FigureCoverageDiff(
                    figure_number=record.number,
                    chapter_path=record.chapter_path or record.chapter_title,
                    diff_type="markdown.missing_image_reference",
                    detail="Figure caption exists in the DOCX inventory but no Markdown image reference points to this figure number.",
                )
            )
            continue

        chapter_match = any(chapter_path == record.chapter_path for chapter_path, _ in refs)
        if not chapter_match:
            diffs.append(
                FigureCoverageDiff(
                    figure_number=record.number,
                    chapter_path=record.chapter_path or record.chapter_title,
                    diff_type="markdown.chapter_mismatch",
                    detail=f"Markdown references exist for Figure {record.number}, but not in the expected chapter file.",
                )
            )

        existing_asset_found = False
        for chapter_path, image_path in refs:
            asset_path = (Path(chapter_path).parent / image_path).resolve()
            if asset_path.exists():
                existing_asset_found = True
            else:
                diffs.append(
                    FigureCoverageDiff(
                        figure_number=record.number,
                        chapter_path=chapter_path,
                        diff_type="assets.missing_file",
                        detail=f"Markdown references missing asset file {image_path}.",
                    )
                )
        if not existing_asset_found:
            diffs.append(
                FigureCoverageDiff(
                    figure_number=record.number,
                    chapter_path=record.chapter_path or record.chapter_title,
                    diff_type="assets.no_existing_reference_target",
                    detail="All Markdown image references for this figure point to files that do not exist on disk.",
                )
            )

    for number, refs in sorted(markdown_refs.items()):
        if number in record_by_number:
            continue
        chapter_path, image_path = refs[0]
        diffs.append(
            FigureCoverageDiff(
                figure_number=number,
                chapter_path=chapter_path,
                diff_type="markdown.untracked_image_reference",
                detail=f"Markdown references {image_path}, but the figure number is absent from the DOCX manifest.",
            )
        )

    manifest_candidates = {record.number: set(record.published_assets) for record in records}
    for record in records:
        if record.published_assets:
            continue
        diffs.append(
            FigureCoverageDiff(
                figure_number=record.number,
                chapter_path=record.chapter_path or record.chapter_title,
                diff_type="manifest.no_asset_candidates",
                detail="No existing files under the edition image root match this figure number prefix.",
            )
        )

    return diffs


def main() -> int:
    args = parse_args()
    edition = get_edition(args.edition) if args.edition else None
    docx_path = Path(args.docx) if args.docx else edition.docx_path if edition else DEFAULT_DOCX
    summary_path = (
        Path(args.summary) if args.summary else edition.summary_path if edition else DEFAULT_SUMMARY
    )
    chapters_dir = (
        Path(args.chapters_dir)
        if args.chapters_dir
        else edition.chapter_root
        if edition
        else DEFAULT_CHAPTERS_DIR
    )
    manifest_path = (
        Path(args.manifest)
        if args.manifest
        else edition.figure_manifest_path
        if edition
        else DEFAULT_MANIFEST
    )
    if manifest_path.exists():
        records = _load_manifest(manifest_path)
    else:
        records = build_figure_inventory(
            docx_path=docx_path,
            chapters_dir=chapters_dir,
            summary_path=summary_path,
        )

    chapter_paths = _chapter_paths(summary_path)
    markdown_refs = _markdown_image_refs(chapter_paths)
    diffs = _coverage_diffs(
        records=records,
        markdown_refs=markdown_refs,
        images_root=chapters_dir.parent / "images",
    )
    if diffs:
        print(
            render_figure_coverage_json(diffs)
            if args.json
            else render_figure_coverage_text(diffs)
        )
        return 1

    print("DOCX figure coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
