from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.edition_config import available_edition_locales, get_edition
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
DEFAULT_SUMMARY = Path("editions/en/content/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("editions/en/content/chapters")
DEFAULT_OUTPUT_DIR = Path("editions/en/content/images")
LOSSLESS_WEBP_FIGURES = {17, 19, 21, 22, 23, 24, 25, 27, 28, 29, 31, 32}


def find_cwebp_binary() -> Path | None:
    resolved = shutil.which("cwebp")
    if resolved:
        return Path(resolved)
    for candidate in (Path("/opt/homebrew/bin/cwebp"), Path("/usr/local/bin/cwebp")):
        if candidate.exists():
            return candidate
    return None


def find_sips_binary() -> Path | None:
    resolved = shutil.which("sips")
    if resolved:
        return Path(resolved)
    candidate = Path("/usr/bin/sips")
    if candidate.exists():
        return candidate
    return None


def ensure_lossless_webp_outputs(
    *,
    output_dir: Path,
    figure_numbers: list[int],
    cwebp_binary: Path | None = None,
    sips_binary: Path | None = None,
) -> list[int]:
    binary = cwebp_binary or find_cwebp_binary()
    sips = sips_binary or find_sips_binary()
    if binary is None:
        if sips is None:
            return []

    rendered: list[int] = []
    for figure_number in figure_numbers:
        if figure_number not in LOSSLESS_WEBP_FIGURES:
            continue
        png_path = output_dir / f"figure-{figure_number:03d}.png"
        webp_path = output_dir / f"figure-{figure_number:03d}.webp"
        if not png_path.exists():
            continue
        if binary is not None:
            result = subprocess.run(
                [
                    str(binary),
                    "-quiet",
                    "-lossless",
                    "-z",
                    "9",
                    str(png_path),
                    "-o",
                    str(webp_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            result = subprocess.run(
                [
                    str(sips),
                    "-s",
                    "format",
                    "webp",
                    str(png_path),
                    "--out",
                    str(webp_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        if result.returncode == 0 and webp_path.exists():
            rendered.append(figure_number)
    return rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render PDF-derived figure assets for DOCX shape/chart/composite figures."
    )
    parser.add_argument("--edition", choices=available_edition_locales())
    parser.add_argument("--pdf")
    parser.add_argument("--docx")
    parser.add_argument("--summary")
    parser.add_argument("--chapters-dir")
    parser.add_argument("--output-dir")
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
    edition = get_edition(args.edition) if args.edition else None
    pdf_path = Path(args.pdf) if args.pdf else edition.pdf_path if edition else DEFAULT_PDF
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
    requested = list(args.figures or [])
    if not requested:
        inventory = build_figure_inventory(
            docx_path=docx_path,
            chapters_dir=chapters_dir,
            summary_path=summary_path,
        )
        requested = default_pdf_figure_numbers(inventory)

    if not requested:
        print("No PDF-renderable figures were selected.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    result = render_pdf_figures(
        pdf_path=pdf_path,
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
    if result.returncode == 0:
        rendered_webp = ensure_lossless_webp_outputs(
            output_dir=output_dir,
            figure_numbers=requested,
        )
        for figure_number in rendered_webp:
            print(
                f"Rendered Figure {figure_number} -> "
                f"{(output_dir / f'figure-{figure_number:03d}.webp').resolve()}"
            )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
