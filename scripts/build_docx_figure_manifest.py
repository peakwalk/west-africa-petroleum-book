from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.docx_figures import build_figure_inventory

DEFAULT_DOCX = Path(
    "resources/Exploration and Exploitation of Petroleum Resources in West Africa (Matt Edited).docx"
)
DEFAULT_SUMMARY = Path("src/SUMMARY.md")
DEFAULT_CHAPTERS_DIR = Path("src/chapters")
DEFAULT_OUTPUT = Path("src/images/figure-manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a DOCX-derived figure inventory manifest."
    )
    parser.add_argument("--docx", default=str(DEFAULT_DOCX))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--chapters-dir", default=str(DEFAULT_CHAPTERS_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = build_figure_inventory(
        docx_path=Path(args.docx),
        chapters_dir=Path(args.chapters_dir),
        summary_path=Path(args.summary),
    )
    output_path = Path(args.output)
    output_path.write_text(
        json.dumps([asdict(record) for record in inventory], indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(inventory)} figure records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
