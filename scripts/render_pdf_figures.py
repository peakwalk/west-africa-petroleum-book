from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_figures import build_figure_inventory
from scripts.docx_figures.pdf_figures import (
    DEFAULT_CAPTION_GAP,
    DEFAULT_CROP_PADDING,
    DEFAULT_INTER_FIGURE_GAP,
    DEFAULT_RENDER_SCALE,
    DEFAULT_SIDE_MARGIN,
    DEFAULT_TOP_MARGIN,
    default_pdf_figure_numbers,
    render_pdf_figures,
)

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_PDF = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).pdf"
)
DEFAULT_SUMMARY = Path("src/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("src/chapters")
DEFAULT_OUTPUT_DIR = Path("src/images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render PDF-derived figure assets for DOCX shape/chart/composite figures."
    )
    parser.add_argument("--pdf", default=str(DEFAULT_PDF))
    parser.add_argument("--docx", default=str(DEFAULT_DOCX))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--chapters-dir", default=str(DEFAULT_CHAPTERS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--figures",
        nargs="*",
        type=int,
        help="Optional subset of figure numbers to render from the PDF.",
    )
    parser.add_argument("--scale", type=float, default=DEFAULT_RENDER_SCALE)
    parser.add_argument("--side-margin", type=float, default=DEFAULT_SIDE_MARGIN)
    parser.add_argument("--top-margin", type=float, default=DEFAULT_TOP_MARGIN)
    parser.add_argument("--caption-gap", type=float, default=DEFAULT_CAPTION_GAP)
    parser.add_argument("--inter-figure-gap", type=float, default=DEFAULT_INTER_FIGURE_GAP)
    parser.add_argument("--crop-padding", type=float, default=DEFAULT_CROP_PADDING)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested = list(args.figures or [])
    if not requested:
        inventory = build_figure_inventory(
            docx_path=Path(args.docx),
            chapters_dir=Path(args.chapters_dir),
            summary_path=Path(args.summary),
        )
        requested = default_pdf_figure_numbers(inventory)

    if not requested:
        print("No PDF-renderable figures were selected.")
        return 0

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = render_pdf_figures(
        pdf_path=Path(args.pdf),
        output_dir=output_dir,
        figure_numbers=requested,
        scale=args.scale,
        side_margin=args.side_margin,
        top_margin=args.top_margin,
        caption_gap=args.caption_gap,
        inter_figure_gap=args.inter_figure_gap,
        crop_padding=args.crop_padding,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
