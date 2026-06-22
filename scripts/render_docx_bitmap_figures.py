from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
from scripts.docx_figures import build_figure_inventory
from scripts.docx_figures.bitmap_media import render_bitmap_figure_assets
from scripts.docx_figures.raster_assets import ensure_lossless_webp_outputs

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("editions/en/content/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("editions/en/content/chapters")
DEFAULT_OUTPUT_DIR = Path("editions/en/content/images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract embedded DOCX bitmap figures into published image assets."
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
        help="Optional subset of figure numbers to extract.",
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
    requested = set(args.figures or [])
    inventory = build_figure_inventory(
        docx_path=docx_path,
        chapters_dir=chapters_dir,
        summary_path=summary_path,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    records = [
        record
        for record in inventory
        if not requested or record.number in requested
    ]
    outputs = render_bitmap_figure_assets(
        docx_path=docx_path,
        records=records,
        output_dir=output_dir,
    )
    for figure_number, output_path in outputs:
        print(f"Rendered Figure {figure_number} -> {output_path}")

    rendered_webp = ensure_lossless_webp_outputs(
        output_dir=output_dir,
        figure_numbers=sorted({figure_number for figure_number, _ in outputs}),
    )
    for figure_number in rendered_webp:
        print(
            f"Rendered Figure {figure_number} -> "
            f"{(output_dir / f'figure-{figure_number:03d}.webp').resolve()}"
        )

    print(f"Rendered {len(outputs)} bitmap asset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
