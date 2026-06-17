from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
from scripts.docx_figures import build_figure_inventory
from scripts.docx_figures.shape_svg import render_shape_figure_svg

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("editions/en/content/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("editions/en/content/chapters")
DEFAULT_OUTPUT_DIR = Path("editions/en/content/images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render DOCX shape-group figures into SVG assets."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--output-dir")
    parser.add_argument(
        "--figures",
        nargs="*",
        type=int,
        help="Optional subset of figure numbers to render.",
    )
    return parser.parse_args()


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
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else edition.figure_root
        if edition
        else DEFAULT_OUTPUT_DIR
    )
    inventory = build_figure_inventory(
        docx_path=docx_path,
        chapters_dir=chapters_dir,
        summary_path=summary_path,
    )
    requested = set(args.figures or [])
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    for record in inventory:
        if record.kind not in {"shape_group", "composite"}:
            continue
        if requested and record.number not in requested:
            continue
        svg = render_shape_figure_svg(
            docx_path,
            paragraph_start=record.object_paragraph_start,
            paragraph_end=record.caption_paragraph_index,
        )
        output_path = output_dir / f"figure-{record.number:03d}.svg"
        output_path.write_text(svg, encoding="utf-8")
        rendered += 1
        print(f"Rendered Figure {record.number} -> {output_path}")

    print(f"Rendered {rendered} shape figure(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
