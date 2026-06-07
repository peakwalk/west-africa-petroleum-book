from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_figures import build_figure_inventory
from scripts.docx_figures.chart_svg import parse_chart_part, render_chart_svg

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("src/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("src/chapters")
DEFAULT_OUTPUT_DIR = Path("src/images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render DOCX chart figures into SVG assets."
    )
    parser.add_argument("--docx", default=str(DEFAULT_DOCX))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--chapters-dir", default=str(DEFAULT_CHAPTERS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--figures",
        nargs="*",
        type=int,
        help="Optional subset of figure numbers to render.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = build_figure_inventory(
        docx_path=Path(args.docx),
        chapters_dir=Path(args.chapters_dir),
        summary_path=Path(args.summary),
    )
    requested = set(args.figures or [])
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered = 0
    for record in inventory:
        if record.kind != "chart":
            continue
        if requested and record.number not in requested:
            continue
        if not record.objects.chart_targets:
            raise ValueError(f"Figure {record.number} is classified as chart but has no chart target.")
        chart = parse_chart_part(Path(args.docx), record.objects.chart_targets[0])
        svg = render_chart_svg(chart)
        output_path = output_dir / f"figure-{record.number:03d}.svg"
        output_path.write_text(svg, encoding="utf-8")
        rendered += 1
        print(f"Rendered Figure {record.number} -> {output_path}")

    if requested and rendered != len(requested):
        missing = sorted(requested.difference({record.number for record in inventory if record.kind == 'chart'}))
        if missing:
            print(f"Warning: requested non-chart or unknown figures were skipped: {missing}")

    print(f"Rendered {rendered} chart figure(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
